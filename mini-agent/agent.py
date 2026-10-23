from fake_llm import get_next_action
from tools import execute_tool

MAX_STEPS = 5


def initialize_history(user_input):
    """Start the conversation history with the user's message."""
    return [{"role": "user", "content": user_input}]


def is_valid_action(action):
    """Check that the LLM returned a well-formed action."""
    if not isinstance(action, dict):
        return False
    if action.get("type") == "final_answer":
        return isinstance(action.get("content"), str)
    if action.get("type") == "tool_call":
        return isinstance(action.get("tool_name"), str) and isinstance(
            action.get("arguments"), dict
        )
    return False


def process_tool_call(action, history):
    """Run the requested tool and record both the call and its result."""
    tool_name = action["tool_name"]
    arguments = action["arguments"]
    history.append({"role": "tool_call", "tool_name": tool_name, "arguments": arguments})

    # execute_tool never raises; errors come back as {"status": "error", ...}
    result = execute_tool(tool_name, arguments)
    history.append({"role": "tool_result", "tool_name": tool_name, "result": result})
    return result


def run_agent(user_input):
    """Run the agent loop and return (final_answer, history)."""
    history = initialize_history(user_input)

    # Agent loop: ask the LLM, act, repeat until a final answer or the step limit
    for _ in range(MAX_STEPS):
        action = get_next_action(history)

        if not is_valid_action(action):
            answer = "Error: the model returned an invalid action."
            history.append({"role": "error", "content": answer})
            return answer, history

        if action["type"] == "final_answer":
            history.append({"role": "assistant", "content": action["content"]})
            return action["content"], history

        process_tool_call(action, history)

    answer = f"Stopped: no final answer after {MAX_STEPS} steps."
    history.append({"role": "error", "content": answer})
    return answer, history
