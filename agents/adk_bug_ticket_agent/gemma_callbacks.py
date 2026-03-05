"""Gemma 3 function calling support via ADK after_model_callback.

This module implements text-based function calling for Gemma 3, which uses
```tool_code``` and ```tool_output``` blocks instead of native function calling.
The after_model_callback intercepts model output, detects tool calls, executes
them safely via ast.parse (no eval), and returns the result for the next LLM turn.
"""

import ast
import inspect
import logging
import re
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse
from google.genai import types

logger = logging.getLogger(__name__)

# Strict regex: ONLY match ```tool_code blocks.
# We intentionally do NOT match ```python or bare ``` because Gemma
# hallucinates fake tool_output blocks and code definitions in those.
_TOOL_CODE_PATTERN = re.compile(
    r"```tool_code\s*\n(.*?)\n\s*```", re.DOTALL
)


def generate_tool_signatures(tools: list) -> str:
    """Generate Python-style function signatures for all tools.

    Produces the text block that gets embedded into the Gemma system prompt,
    so the model knows which tools are available and how to call them.

    Args:
        tools: List of tool callables (LazyToolboxTool, functions, etc.)

    Returns:
        A string of Python function signatures with docstrings.
    """
    signatures = []
    for tool in tools:
        try:
            name = tool.__name__.replace("-", "_")
            doc = tool.__doc__ or "No description available."
            sig = inspect.signature(tool)

            # Build parameter list with type annotations
            params = []
            for param_name, param in sig.parameters.items():
                if param.annotation != inspect.Parameter.empty:
                    annotation = (
                        param.annotation.__name__
                        if hasattr(param.annotation, "__name__")
                        else str(param.annotation)
                    )
                    params.append(f"{param_name}: {annotation}")
                else:
                    params.append(param_name)

            params_str = ", ".join(params)
            sig_str = f"def {name}({params_str}) -> dict:\n"
            sig_str += f'    """{doc.strip()}\n    """'
            signatures.append(sig_str)
        except (ValueError, TypeError) as e:
            logger.warning(f"Could not generate signature for tool {tool}: {e}")
            continue

    return "\n\n".join(signatures)


def _build_tool_map(tools: list) -> dict:
    """Build name->callable map with both hyphen and underscore variants.

    Args:
        tools: List of tool callables.

    Returns:
        Dict mapping tool names (both hyphenated and underscored) to callables.
    """
    tool_map = {}
    for tool in tools:
        try:
            name = tool.__name__  # e.g. "search-tickets"
            tool_map[name] = tool  # "search-tickets" -> callable
            tool_map[name.replace("-", "_")] = tool  # "search_tickets" -> callable
        except AttributeError:
            logger.warning(f"Tool {tool} has no __name__ attribute, skipping.")
    return tool_map


def _extract_tool_call(code_block: str, tool_map: dict) -> Optional[str]:
    """Extract the first recognized tool function call from a code block.

    Gemma may output function definitions, assignments, or other code alongside
    the actual tool call. This scans each statement/expression for a call to
    a known tool function.

    Args:
        code_block: The raw code string from inside the fenced block.
        tool_map: Dict mapping tool names to callables.

    Returns:
        The matching call expression as a string, or None if not found.
    """
    try:
        tree = ast.parse(code_block.strip(), mode="exec")
    except SyntaxError:
        # Fall back to single-expression parse
        try:
            tree = ast.parse(code_block.strip(), mode="eval")
            if isinstance(tree.body, ast.Call):
                call = tree.body
                name = getattr(call.func, "id", None) or getattr(call.func, "attr", None)
                if name and name in tool_map:
                    return code_block.strip()
        except SyntaxError:
            pass
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if name and name in tool_map:
                return ast.unparse(node)
    return None


def _safe_execute_tool(tool_code_str: str, tool_map: dict) -> str:
    """Safely parse and execute a tool call from Gemma's tool_code output.

    Uses ast.parse to extract function name and arguments - NO eval().
    Validates the function name against the tool_map allowlist.
    Uses ast.literal_eval for each argument value (safe for strings, numbers,
    lists, dicts).

    Args:
        tool_code_str: The raw code string from the tool_code block,
                       e.g. 'search_tickets(query="login")'
        tool_map: Dict mapping tool names to callables.

    Returns:
        String representation of the tool result.
    """
    try:
        tree = ast.parse(tool_code_str.strip(), mode="eval")
    except SyntaxError as e:
        return f"Error: Could not parse tool code: {e}"

    # Expect a single Call expression
    if not isinstance(tree.body, ast.Call):
        return "Error: Expected a function call expression."

    call_node = tree.body

    # Extract function name
    if isinstance(call_node.func, ast.Name):
        func_name = call_node.func.id
    elif isinstance(call_node.func, ast.Attribute):
        func_name = call_node.func.attr
    else:
        return "Error: Unsupported function call format."

    # Validate against allowlist
    if func_name not in tool_map:
        return f"Error: Unknown function '{func_name}'. Available: {list(tool_map.keys())}"

    # Extract arguments
    kwargs = {}
    try:
        # Handle keyword arguments
        for kw in call_node.keywords:
            kwargs[kw.arg] = ast.literal_eval(kw.value)

        # Handle positional arguments
        args = [ast.literal_eval(arg) for arg in call_node.args]
    except (ValueError, TypeError) as e:
        return f"Error: Could not evaluate arguments: {e}"

    # Execute the tool
    try:
        tool = tool_map[func_name]
        if args and kwargs:
            result = tool(*args, **kwargs)
        elif args:
            result = tool(*args)
        else:
            result = tool(**kwargs)
        return str(result)
    except Exception as e:
        logger.error(f"Tool execution error for {func_name}: {e}")
        return f"Error executing {func_name}: {e}"


# Module-level tool map, set during agent initialization
_tool_map: dict = {}
# List of available tool names (underscore format) for corrective feedback
_available_tool_names: list = []


def set_tool_map(tools: list) -> None:
    """Initialize the module-level tool map from a list of tools.

    Called once during agent initialization to make tools available
    to the callback.

    Args:
        tools: List of tool callables.
    """
    global _tool_map, _available_tool_names
    _tool_map = _build_tool_map(tools)
    # Deduplicated underscore-format names for corrective messages
    _available_tool_names = sorted(set(
        k.replace("-", "_") for k in _tool_map.keys()
    ))
    logger.info(f"Gemma tool map initialized with {len(_tool_map)} entries: {list(_tool_map.keys())}")


def after_model_gemma_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> Optional[LlmResponse]:
    """ADK after_model_callback for Gemma 3 text-based function calling.

    Inspects the model response for ```tool_code``` blocks. If found, safely
    executes the tool and returns a new LlmResponse with the tool_output
    appended, triggering another model turn with the result in context.

    If no tool_code block is found, returns None (normal ADK flow continues).

    Args:
        callback_context: The ADK callback context.
        llm_response: The LLM response to inspect.

    Returns:
        A new LlmResponse with tool output if a tool call was detected,
        or None if no tool call was found.
    """
    if not llm_response or not llm_response.content or not llm_response.content.parts:
        return None

    # Combine all text parts
    full_text = ""
    for part in llm_response.content.parts:
        if part.text:
            full_text += part.text

    if not full_text:
        return None

    logger.info(f"after_model_gemma_callback full text (first 500 chars): {full_text[:500]}")

    # Strictly match only ```tool_code blocks
    match = _TOOL_CODE_PATTERN.search(full_text)
    if not match:
        # Check if the model generated any code block at all (wrong format)
        has_any_code_block = re.search(r"```(?:python)?\s*\n", full_text)
        if has_any_code_block:
            # Model tried to use code but with wrong marker — send correction
            logger.info("Detected code block with wrong marker, sending corrective feedback.")
            correction = (
                "You used the wrong format. You MUST use ```tool_code``` blocks, "
                "not ```python``` or ``` blocks. Also, you must CALL an existing "
                "function, not define a new one.\n\n"
                f"Available functions: {', '.join(_available_tool_names)}\n\n"
                "Example:\n```tool_code\n"
                "get_tickets_by_status(status=\"Open\")\n```"
            )
            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[types.Part(text=correction)],
                )
            )
        return None

    code_block = match.group(1).strip()
    logger.info(f"Gemma tool_code block detected: {code_block}")

    # Extract the actual tool call from the code block
    tool_call_str = _extract_tool_call(code_block, _tool_map)
    if not tool_call_str:
        # tool_code block but no recognized function — send correction
        correction = (
            "ERROR: The function you called is not available. "
            f"You must call one of: {', '.join(_available_tool_names)}\n\n"
            "Example:\n```tool_code\n"
            "search_tickets(query=\"login bug\")\n```"
        )
        logger.info("Corrective feedback: unrecognized function in tool_code block.")
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text=correction)],
            )
        )

    logger.info(f"Extracted tool call: {tool_call_str}")

    # Execute the tool safely
    tool_result = _safe_execute_tool(tool_call_str, _tool_map)
    logger.info(f"Tool result: {tool_result[:500]}")

    # Return ONLY the tool_output — keep it clean for the next model turn
    tool_output_text = f"```tool_output\n{tool_result}\n```"

    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part(text=tool_output_text)],
        )
    )
