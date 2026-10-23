import re

# Matches simple expressions such as "12 * 7", "-3.5 + 2" or "10/4"
CALCULATION_PATTERN = re.compile(r"(-?\d+(?:\.\d+)?)\s*([+\-*/])\s*(-?\d+(?:\.\d+)?)")

TIME_KEYWORDS = ("time", "clock", "hour")


def to_number(text):
    """Convert numeric text to int when possible, otherwise float."""
    return float(text) if "." in text else int(text)


def parse_calculation(text):
    """Return calculator arguments found in the text, or None."""
    match = CALCULATION_PATTERN.search(text)
    if not match:
        return None
    left, operator, right = match.groups()
    return {"a": to_number(left), "b": to_number(right), "operator": operator}


def decide_from_user_message(text):
    """Choose a tool call (or a refusal) based on the user's request."""
    arguments = parse_calculation(text)
    if arguments:
        return {"type": "tool_call", "tool_name": "calculate", "arguments": arguments}

    if any(word in text.lower() for word in TIME_KEYWORDS):
        return {"type": "tool_call", "tool_name": "get_current_time", "arguments": {}}

    return {
        "type": "final_answer",
        "content": "Sorry, I can only do simple calculations or tell the time.",
    }


def answer_from_tool_result(entry):
    """Turn the latest tool result into a final answer."""
    result = entry["result"]
    if result["status"] == "error":
        return {"type": "final_answer", "content": f"The tool failed: {result['message']}."}

    if entry["tool_name"] == "get_current_time":
        return {"type": "final_answer", "content": f"The current time is {result['value']}."}
    return {"type": "final_answer", "content": f"The result is {result['value']}."}


def get_next_action(history):
    """Simulate an LLM: read the history and decide the next action."""
    last_entry = history[-1]

    # A fresh user message means we still need to decide what to do
    if last_entry["role"] == "user":
        return decide_from_user_message(last_entry["content"])

    # A tool just answered, so we can now reply to the user
    if last_entry["role"] == "tool_result":
        return answer_from_tool_result(last_entry)

    return {"type": "final_answer", "content": "I am not sure what to do next."}
