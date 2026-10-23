from datetime import datetime


def calculate(a, b, operator):
    """Apply a basic arithmetic operator to two numbers."""
    # Reject booleans and non-numbers before doing any math
    for value in (a, b):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"'{value}' is not a number")

    if operator == "+":
        return a + b
    if operator == "-":
        return a - b
    if operator == "*":
        return a * b
    if operator == "/":
        if b == 0:
            raise ValueError("division by zero")
        return a / b
    raise ValueError(f"unsupported operator '{operator}'")


def get_current_time():
    """Return the current local time as a readable string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Tool registry: maps each tool name to its function and expected argument names
TOOLS = {
    "calculate": {"function": calculate, "params": ["a", "b", "operator"]},
    "get_current_time": {"function": get_current_time, "params": []},
}


def validate_tool_call(tool_name, arguments):
    """Return an error message if the call is invalid, otherwise None."""
    if tool_name not in TOOLS:
        return f"unknown tool '{tool_name}'"
    if not isinstance(arguments, dict):
        return "arguments must be a dictionary"

    expected = set(TOOLS[tool_name]["params"])
    if set(arguments) != expected:
        return f"expected arguments {sorted(expected)}, got {sorted(arguments)}"
    return None


def execute_tool(tool_name, arguments):
    """Validate and run a tool, always returning a result dictionary."""
    error = validate_tool_call(tool_name, arguments)
    if error:
        return {"status": "error", "message": error}

    function = TOOLS[tool_name]["function"]
    try:
        # Unpack the dictionary as keyword arguments, e.g. calculate(a=1, b=2, operator="+")
        return {"status": "success", "value": function(**arguments)}
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}
