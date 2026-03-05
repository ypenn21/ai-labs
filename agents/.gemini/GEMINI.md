# GEMINI.MD: AI Collaboration Guide

This document provides essential context for AI models interacting with this project. Adhering to these guidelines will ensure consistency and maintain code quality.

## 1. Project Overview & Purpose

* **Primary Goal:** This project is a Python-based Restaurant Order Assistant agent built using the Google Agent Development Kit (ADK). It is designed to interpret natural language user inputs to detect orders, manage menus, and suggest responses.
* **Business Domain:** Food Service / Restaurant Technology (AI Order Taking).

## 2. Core Technologies & Stack

* **Languages:** Python 3 (Specific version inferred: 3.8+ based on type hinting and `venv` usage).
* **Frameworks & Runtimes:** 
    * **Google ADK (Agent Development Kit):** Core framework for building the agent.
    * **A2A SDK:** Agent-to-Agent communication standard.
    * **Starlette:** Used via A2A SDK for serving the agent (implied by `A2AStarletteApplication`).
* **Databases:**
    * **Primary:** In-Memory storage (`InMemorySessionService`, `InMemoryMemoryService`) for current configuration.
    * **Future/Optional:** PostgreSQL (supported by `DatabaseSessionService`, referenced in code comments).
* **Key Libraries/Dependencies:**
    * `google-adk`: Main agent framework.
    * `a2a-sdk`: For agent interoperability.
    * `litellm`: For model abstraction and interface.
    * `pydantic`: For data validation and settings management.
* **Package Manager(s):** `pip` (dependency management via `requirements.txt`).

## 3. Architectural Patterns

* **Overall Architecture:** **Agent-Executor Pattern** with a **Service Manager**.
    * The system uses a `ServiceManager` class (`app/agent.py`) to lazy-load and manage singleton instances of services (Session, Memory, Agent).
    * It implements the Google ADK `Runner` pattern for executing the agent loop.
* **Directory Structure Philosophy:**
    * `/app`: Contains the core application logic.
        * `agent.py`: Configuration and initialization of the Agent and Services.
        * `strategies.py`: Contains system prompts (`ORDER_DETECTION_SYSTEM_PROMPT`) and core business logic functions.
        * `tools.py`: Definitions of tools available to the agent (e.g., date, search).
        * `agent_executor.py`: Adapts the ADK agent for A2A execution.
    * `/plan`: Contains documentation and optimization plans.
    * Root (`/`): Contains entry points and verification scripts.

## 4. Coding Conventions & Style Guide

* **Formatting:** Python standard (PEP 8 inferred). Indentation is 4 spaces.
* **Naming Conventions:**
    * `variables`, `functions`: snake_case (e.g., `get_agent`, `analyze_order_summary`).
    * `classes`: PascalCase (e.g., `ServiceManager`, `InMemorySessionService`).
    * `constants`: UPPER_CASE (e.g., `ORDER_DETECTION_SYSTEM_PROMPT`, `AGENT_PORT`).
* **API Design:** 
    * The agent exposes an A2A (Agent-to-Agent) compatible interface.
    * Supports JSON-RPC via Starlette (when running as a server).
* **Error Handling:**
    * `try...catch` blocks used in the main run loop (`main.py`) to handle `KeyboardInterrupt` and general exceptions.
    * Tracebacks are printed for debugging.

## 5. Key Files & Entrypoints

* **Main Entrypoint(s):** 
    * `main.py`: CLI entry point for running the agent locally.
    * `app/agent.py`: Core configuration file for initializing the agent and its services.
* **Configuration:**
    * Environment variables are the primary configuration method (e.g., `GOOGLE_CLOUD_PROJECT`, `GOOGLE_API_KEY`, `AGENT_MODE`).
    * `requirements.txt`: Python dependency definitions.
* **Verification:**
    * `verify.py`: A script to run automated verification tests against the agent (e.g., testing greeting and order flows).

## 6. Development & Testing Workflow

* **Local Development Environment:**
    1. Create a virtual environment: `python3 -m venv venv`.
    2. Activate it: `source venv/bin/activate`.
    3. Install dependencies: `pip install -r requirements.txt`.
    4. Set required environment variables (Google Cloud Project, API Key).
    5. Run the agent: `python main.py`.
* **Testing:**
    * Run verification tests using `python verify.py`.
    * Manual testing via the CLI interface in `main.py`.
* **CI/CD Process:** Not explicitly defined in this directory. Relies on manual verification and potentially parent repository workflows.

## 7. Specific Instructions for AI Collaboration

* **Prompt Engineering:** modifications to the agent's behavior should primarily happen in `app/strategies.py` by updating `ORDER_DETECTION_SYSTEM_PROMPT` or `RESPONSE_SUGGESTION_SYSTEM_PROMPT`.
* **Tool Definition:** New tools should be defined in `app/tools.py` and registered in the `Agent` configuration in `app/agent.py`.
* **State Management:** The project currently defaults to `InMemorySessionService`. When discussing persistence, be aware that `DatabaseSessionService` is available but not currently active in the default `ServiceManager` configuration.
* **Environment:** Always remind the user to set `GOOGLE_CLOUD_PROJECT` and `GOOGLE_API_KEY` (or `GOOGLE_CLOUD_LOCATION` for Vertex AI) if they encounter authentication errors.


## 7. Google Gemma 3 Function Calling Example
March 14, 2025
8 minute read
View Code
Google Gemma 3 27B It is an open, multilingual, multimodal Vision-Language model. It handles context windows up to 128k tokens, understands over 140 languages, and offers improved math, reasoning, and chat capabilities, including structured outputs and function calling.

Gemma 3 can be used for agentic workflows and has very strong instruction following capabilities. While there are no dedicated tool/function calling special tokens, you can prompt it to do function calling through careful instruction. Gemma 3 27B is available via AI Studio and the Gen AI API. Get your API key from AI Studio.

Function calling is the capability to connect LLMs to external tools and to interact with your code and APIs in a structured way. Instead of generating text responses, LLMs understand when to call specific functions and provide the necessary parameters to execute real-world actions.

Function calling

Function Calling follows these steps:

Your application sends a prompt to the LLM along with function definitions
The LLM analyzes the prompt and decides whether to respond directly or use defined functions
If using functions, the LLM generates structured arguments for the function call
Your application receives the function call details and executes the actual function
The function results are sent back to the LLM
The LLM provides a final response incorporating the function results
Raw Text Example of how function calling can be implement with Gemma 3
Below is an textual example of how to use function calling with Gemma 3 27B It. In this example the first user message includes the general instruction how and when to use function calling and example flow. The prompt with the Gemma 3 template would look like this:

Send user message with instructions and function definitons and first user message.

<bos><start_of_turn>user
At each turn, if you decide to invoke any of the function(s), it should be wrapped with ```tool_code```. The python methods described below are imported and available, you can only use defined methods. The generated code should be readable and efficient. The response to a method will be wrapped in ```tool_output``` use it to call more tools or generate a helpful, friendly response. When using a ```tool_call``` think step by step why and how it should be used.

The following Python methods are available:

\`\`\`python
def convert(amount: float, currency: str, new_currency: str) -> float:
    """Convert the currency with the latest exchange rate

    Args:
      amount: The amount of currency to convert
      currency: The currency to convert from
      new_currency: The currency to convert to
    """
\`\`\`


User: What is $200,000 in EUR?<end_of_turn>
<start_of_turn>model
Note: The ``` should not be escaped when you use it, but my blog cannot render ``` inside a code block. See code.

Handle Model response when a tool/function is used.

Okay, I need to convert $200,000 to EUR. I will use the `convert` function for this.
\`\`\`tool_code
convert(amount=200000.0, currency="USD", new_currency="EUR")
\`\`\`
Execute local function and create tool output string

\`\`\`tool_output
180000.0
\`\`\`
Send the tool output as new request to the model

<bos><start_of_turn>user
At each turn, if you decide to invoke any of the function(s), it should be wrapped with ```tool_code```. The python methods described below are imported and available, you can only use defined methods. The generated code should be readable and efficient. The response to a method will be wrapped in ```tool_output``` use it to call more tools or generate a helpful, friendly response. When using a ```tool_call``` think step by step why and how it should be used.

The following Python methods are available:

\`\`\`python
def convert(amount: float, currency: str, new_currency: str) -> float:
    """Convert the currency with the latest exchange rate

    Args:
      amount: The amount of currency to convert
      currency: The currency to convert from
      new_currency: The currency to convert to
    """
\`\`\`

User: What is $200,000 in EUR?<end_of_turn>
<start_of_turn>model
Okay, I need to convert $200,000 to EUR. I will use the `convert` function for this.
\`\`\`tool_code
convert(amount=200000.0, currency="USD", new_currency="EUR")
\`\`\`<end_of_turn>
<start_of_turn>user
\`\`\`tool_output
180000.0
\`\`\`<end_of_turn>
<start_of_turn>model
Final Response: $200,000 is approximately €180,000
Function Calling Example with Gemma 3 27B and Python.
Now, let's test this using the GenAI API. If you want to do this locally, e.g. ollama. You can just use the prompts and simulate the function execution. So first install the google-genai SDK.


%pip install google-genai
Then we create our client, define Gemma as model id and create a helper method extract_tool_call. This method parses the model responses and checks if there is a ```tool_code```. If there is one it uses the eval method to run it, extract the result and create a ```tool_output```.

Note: We use eval only for demonstration purposes if you plan to use this in production you should add more security and safety as it will execute model generated code in your environment.


import os
from google import genai
import re 
# create client
api_key = os.getenv("GEMINI_API_KEY","xxx")
client = genai.Client(api_key=api_key)
 
# speicfy the model id
model_id = "gemma-3-27b-it"
 
# extract the tool call from the response
def extract_tool_call(text):
    import io
    from contextlib import redirect_stdout
 
    pattern = r"```tool_code\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        code = match.group(1).strip()
        # Capture stdout in a string buffer
        f = io.StringIO()
        with redirect_stdout(f):
            result = eval(code)
        output = f.getvalue()
        r = result if output == '' else output
        return f'```tool_output\n{r}\n```'''
    return None
 
Next, we define a simple example for a function we want to use. Here is is a convert method that simulates the conversion calcuation of currencies. Since we use eval the method we want to use for function calling needs to be available in the environment.

We define our first user prompt including our instructions and function signature with a docstring and args and a template string for our user message.


def convert(amount: float, currency: str, new_currency: str) -> float:
  # demo implementation
  return amount * 0.9
 
 
instruction_prompt_with_function_calling = '''At each turn, if you decide to invoke any of the function(s), it should be wrapped with ```tool_code```. The python methods described below are imported and available, you can only use defined methods. The generated code should be readable and efficient. The response to a method will be wrapped in ```tool_output``` use it to call more tools or generate a helpful, friendly response. When using a ```tool_call``` think step by step why and how it should be used.
 
The following Python methods are available:
 
\`\`\`python
def convert(amount: float, currency: str, new_currency: str) -> float:
    """Convert the currency with the latest exchange rate
 
    Args:
      amount: The amount of currency to convert
      currency: The currency to convert from
      new_currency: The currency to convert to
    """
 
def get_exchange_rate(currency: str, new_currency: str) -> float:
    """Get the latest exchange rate for the currency pair
 
    Args:
      currency: The currency to convert from
      new_currency: The currency to convert to
    """
\`\`\`
 
User: \{user_message\}'''
Note: The ``` should not be escaped when you use it, but my blog cannot render ``` inside a code block. See code.

The genai SDK supports stateful chat session, which makes it quite easy to test our example as we can easily append the different messages. First, we start with a simple greeting to see what Gemma does.


chat = client.chats.create(model=model_id)
 
response = chat.send_message(instruction_prompt_with_function_calling.format(user_message="hello"))
print(response.text)
# Hello! How can I help you today? Do you want to convert some currency, or get an exchange rate?
Nice! it greeted us back and didn't use any function call. Okay now lets ask it to convert some currency.


response = chat.send_message("What is $200,000 in EUR?")
print(response.text)
Okay, I need to convert $200,000 to EUR. I will use the `convert` function for this.
# ```tool_code
# convert(amount=200000.0, currency="USD", new_currency="EUR")
# ```
Great! it generated out ```tool_code```, which we can now use and extract and to cool our method.


call_response = extract_tool_call(response.text)
print(call_response)
# ```tool_output
# 180000.0
# ```
After we have the response from our tool call we send a final message to generate a user friendly output.


response = chat.send_message(call_response)
print(response.text)
# $200,000 is equivalent to €180,000. Is there anything else I can help you with?
Conclusion
Function calling enables us to build powerful AI assistants that can access real-time data, perform actions, handle complex interactions, and provide natural language interfaces to APIs and tools, making it an increasingly important capability for practical AI applications that interact with the real world.

This is a simplified example on how you could implement function calling with Gemma 3. I didn't run detailed evaluation or benchmarks. Gemma 3 is an open model with strong reasoning and instruction following capabilities. This allows you to further optimize the prompt used to match your use case and data or further fine-tune on data with similar format to customize its agentic capabilities.
