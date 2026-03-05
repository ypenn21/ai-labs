# Implementation Plan — Gemma 3 Function Calling (Callback Approach)

## 1. 🔍 Analysis & Context
*   **Objective:** Implement function calling for the Gemma 3 model using the text-based `tool_code` and `tool_output` format, leveraging the ADK's `after_model_callback` for an idiomatic implementation.
*   **New File:**
    *   `adk_bug_ticket_agent/gemma_callbacks.py`
*   **Modified Files:**
    *   `adk_bug_ticket_agent/system_prompt.py`
    *   `adk_bug_ticket_agent/agent.py`
*   **Unchanged Files:**
    *   `adk_bug_ticket_agent/agent_executor.py` — no changes needed; ADK handles re-invocation natively.
*   **Key Dependencies:** `google-adk`, `litellm`.

## 2. 📋 Checklist
- [ ] Create `gemma_callbacks.py` (tool signatures, safe execution, after_model_callback).
- [ ] Add `gemma_agent_instruction` to `system_prompt.py`.
- [ ] Add `GEMMA` mode to `AgentMode` enum and `_init_gemma_agent()` to `ServiceManager`.
- [ ] Write unit tests for `_safe_execute_tool` and `generate_tool_signatures`.
- [ ] Manual end-to-end verification.

## 3. 📝 Step-by-Step Implementation Details

### Step 1: Create `gemma_callbacks.py`
*   **Goal:** A self-contained module with three responsibilities.
*   **Action:** Create `adk_bug_ticket_agent/gemma_callbacks.py` with:

    1.  **`generate_tool_signatures(tools: list) -> str`**
        *   Iterates tools from `get_toolbox_tools()` and `get_current_date`.
        *   Formats each tool's `__name__`, `__doc__`, and `__signature__` into the Python docstring format Gemma expects.
        *   Returns a single string block of all tool signatures.

    2.  **`after_model_gemma_callback(callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[LlmResponse]`**
        *   Checks `llm_response` text for a `` ```tool_code ... ``` `` block using regex.
        *   If found: calls `_safe_execute_tool()`, then returns a **new `LlmResponse`** with the `tool_output` appended. The ADK Runner sees this returned `LlmResponse` and uses it, triggering another model turn with the tool output in context.
        *   If not found: returns `None` (normal ADK flow continues).

    3.  **`_safe_execute_tool(tool_code_str: str, tool_map: dict) -> str`**
        *   Uses `ast.parse` to extract the function name and arguments from the code string.
        *   Validates the function name against the `tool_map` allowlist.
        *   Uses `ast.literal_eval` for each argument value (safe for strings, numbers, lists, dicts).
        *   Calls the matched tool and returns the result as a string.

> **Why no changes to `agent_executor.py`?**
> The original plan proposed `GemmaToolCallingError`, a `while` loop, and `try/except` in the executor. This is unnecessary. The ADK `after_model_callback` mechanism handles re-invocation natively — when the callback returns an `LlmResponse`, the ADK Runner replaces the model output for that turn. The tool output is already in the conversation history for the next LLM call. No custom exception flow needed.

### Step 2: Add Gemma System Prompt
*   **Goal:** Create a Gemma-specific prompt in `system_prompt.py` with `tool_code`/`tool_output` instructions.
*   **Action:**
    *   Add a `gemma_agent_instruction` variable containing function calling instructions based on the Gemma 3 format.
    *   Include a `{tool_signatures}` placeholder populated at agent init time.
    *   The existing `agent_instruction` is **not modified**.

### Step 3: Update `agent.py`
*   **Goal:** Wire up the Gemma agent mode using the callback.
*   **Action:**
    *   **Add `GEMMA = "Gemma"` to `AgentMode` enum.**
    *   **Add `_init_gemma_agent()` to `ServiceManager`:**
        ```python
        def _init_gemma_agent(self):
            from .gemma_callbacks import generate_tool_signatures, after_model_gemma_callback
            tools = [get_current_date, search_tool, *get_toolbox_tools()]
            tool_sigs = generate_tool_signatures(tools)
            return Agent(
                model=LiteLlm(model=MODEL_NAME, api_base=api_base_url),
                name="it_bug_assistant_agent",
                instruction=system_prompt.gemma_agent_instruction.format(
                    tool_signatures=tool_sigs
                ),
                tools=tools,
                after_model_callback=after_model_gemma_callback,
            )
        ```
    *   **Add `AgentMode.GEMMA` branch** in the `root_agent` property.

### Architecture Flow

```
User Query
  → A2A Executor (unchanged)
    → ADK Runner
      → Gemma LLM (prompt includes tool signatures in system prompt)
      ← "```tool_code\nsearch_tickets(query='login')\n```"
      → after_model_callback intercepts
        → _safe_execute_tool("search_tickets", tool_map)
        ← Returns LlmResponse with tool_output
      → Gemma LLM (conversation now includes tool_output)
      ← "I found 3 login-related tickets..."
      → after_model_callback: no tool_code → returns None
    ← Final response
  ← User sees result
```

## 4. 🧪 Testing Strategy
*   **Unit Tests** (`tests/test_gemma_callbacks.py`):
    *   `_safe_execute_tool`: simple calls, keyword args, unknown function rejection, malicious code rejection.
    *   `generate_tool_signatures`: valid output for all registered tools.
*   **Integration Tests:** Run the agent with `AGENT_MODE=Gemma` and verify end-to-end tool calling flow.
*   **Manual Verification:**
    1.  Send a greeting — verify no tool call triggered.
    2.  Send "Search for login bug tickets" — verify tool execution and final response.
    3.  Send a multi-step query — verify chained tool calls.

## 5. ✅ Success Criteria
*   The agent successfully uses tools with Gemma 3 via the `after_model_callback` mechanism.
*   The implementation is safe (no `eval()`), idiomatic (uses ADK callback API correctly), and cleanly isolated in `gemma_callbacks.py`.
*   No modifications to `agent_executor.py` are required.
*   The agent can handle multi-step tool calls if required.

## 6. ⚠️ Risks & Open Items
*   **`after_model_callback` re-call behavior:** If returning an `LlmResponse` from the callback doesn't trigger a new LLM turn with the tool output in context, we would need the executor loop approach as a fallback. Validate during testing.
*   **Model endpoint config:** The `MODEL_NAME` and endpoint env vars must point to a running Gemma 3 endpoint (deployed via `deploy_gemma.py`).

## 7. 🔌 MCP Toolbox Integration — Tool Mapping & Invocation

### The Problem: Hyphen vs Underscore Names

MCP Toolbox tools use **hyphenated names** (`search-tickets`, `create-new-ticket`) but Gemma generates **valid Python** with underscores (`search_tickets(query="login")`). The callback must normalize between both formats.

### Tool Map Construction

At agent init, build a `tool_map` dict from the `LazyToolboxTool` objects already loaded by `get_toolbox_tools()`:

```python
def _build_tool_map(tools: list) -> dict:
    """Build name→callable map with both hyphen and underscore variants."""
    tool_map = {}
    for tool in tools:
        name = tool.__name__                   # e.g. "search-tickets"
        tool_map[name] = tool                  # "search-tickets" → callable
        tool_map[name.replace("-", "_")] = tool # "search_tickets" → callable
    return tool_map
```

### Full Invocation Chain

When Gemma generates `` ```tool_code\nsearch_tickets(query="login")\n``` ``, the invocation flows through:

```
after_model_gemma_callback()
  │
  ├─ regex extracts: search_tickets(query="login")
  │
  ├─ ast.parse → func_name="search_tickets", kwargs={"query": "login"}
  │
  ├─ tool_map["search_tickets"]
  │     └─→ LazyToolboxTool (name="search-tickets", toolset="tickets_toolset")
  │
  └─ tool(**kwargs)
        │
        ├─ LazyToolboxTool.__call__(query="login")
        │     └─ _ensure_tool()  # lazy-loads from ToolboxSyncClient if needed
        │
        ├─ ToolboxSyncTool.__call__(query="login")
        │     └─ HTTP POST → MCP Toolbox Server (http://127.0.0.1:5000)
        │
        └─ MCP Toolbox Server
              └─ Executes SQL against PostgreSQL:
                   SELECT ticket_id, title, description, ...
                   FROM tickets
                   ORDER BY (embedding <=> embedding('text-embedding-005', $1)::vector) ASC
                   LIMIT 3;
              └─ Returns JSON result
```

### MCP Tool Signatures for Gemma Prompt

`generate_tool_signatures()` inspects each `LazyToolboxTool` at init and produces what Gemma sees:

```python
# Rendered into the system prompt as:

def search_tickets(query: str) -> dict:
    """Search for similar tickets based on their descriptions.
    Args:
      query: The query to perform vector search with.
    """

def update_ticket_status(status: str, ticket_id: str) -> dict:
    """Update the status of a ticket based on its ID.
    Args:
      status: The new status ('Open', 'In Progress', 'Closed', 'Resolved').
      ticket_id: The ID of the ticket.
    """

def create_new_ticket(title: str, description: str, assignee: str, priority: str, status: str) -> dict:
    """Create a new software ticket.
    Args:
      title: The title of the new ticket.
      description: A detailed description of the bug or issue.
      assignee: (Optional) The email of the assignee.
      priority: (Optional) 'P0 - Critical', 'P1 - High', 'P2 - Medium', 'P3 - Low'. Default 'P3 - Low'.
      status: (Optional) Initial status. Default 'Open'.
    """

# ... all 9 MCP tools + get_current_date
```

> **Note:** Tool names are rendered with underscores in the prompt (valid Python) even though MCP uses hyphens internally. The `tool_map` handles the translation transparently.
