import re

# Matches simple expressions such as "12 * 7", "-3.5 + 2" or "10/4"
CALCULATION_PATTERN = re.compile(r"(-?\d+(?:\.\d+)?)\s*([+\-*/])\s*(-?\d+(?:\.\d+)?)")

TIME_KEYWORDS = ("time", "clock", "hour")


def to_number(text):
    """Convert numeric text to int when possible, otherwise float."""
    return float(text) if "." in text else int(text)


def plan_tool_calls(text):
    """Find every task in the user's message, in the order they appear."""
    found = []  # (position in text, tool call)

    for match in CALCULATION_PATTERN.finditer(text):
        left, operator, right = match.groups()
        arguments = {"a": to_number(left), "b": to_number(right), "operator": operator}
        found.append((match.start(), {"tool_name": "calculate", "arguments": arguments}))

    lowered = text.lower()
    time_positions = [lowered.find(word) for word in TIME_KEYWORDS if word in lowered]
    if time_positions:
        found.append((min(time_positions), {"tool_name": "get_current_time", "arguments": {}}))

    found.sort(key=lambda item: item[0])
    return [call for _, call in found]


def describe_result(entry):
    """Turn one tool result into a sentence."""
    result = entry["result"]
    if result["status"] == "error":
        return f"The tool failed: {result['message']}."
    if entry["tool_name"] == "get_current_time":
        return f"The current time is {result['value']}."
    args = entry["arguments"]
    return f"{args['a']} {args['operator']} {args['b']} = {result['value']}."


def get_next_action(history):
    """Simulate an LLM: read the history and decide the next action."""
    # Find the latest user message; everything after it belongs to this request
    user_index = max(i for i, entry in enumerate(history) if entry["role"] == "user")
    planned = plan_tool_calls(history[user_index]["content"])

    if not planned:
        return {
            "type": "final_answer",
            "content": "Sorry, I can only do simple calculations or tell the time.",
        }

    # Pair each tool result with the call that produced it
    recent = history[user_index + 1:]
    calls = [e for e in recent if e["role"] == "tool_call"]
    results = [e for e in recent if e["role"] == "tool_result"]

    # Some tasks are still waiting: call the next tool
    if len(results) < len(planned):
        return {"type": "tool_call", **planned[len(results)]}

    # Every task is done: combine all results into one answer
    sentences = [
        describe_result({**result, "arguments": call["arguments"]})
        for call, result in zip(calls, results)
    ]
    return {"type": "final_answer", "content": " ".join(sentences)}
