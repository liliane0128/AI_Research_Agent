from agent import run_agent


def print_history(history):
    """Show every step the agent took, in order."""
    step = 0
    for entry in history:
        role = entry["role"]
        # Each tool call or final reply is one pass through the agent loop
        if role in ("tool_call", "assistant", "error"):
            step += 1
            print(f"\n--- Step {step} ---")

        if role == "tool_call":
            print(f"Tool call:   {entry['tool_name']}({entry['arguments']})")
        elif role == "tool_result":
            print(f"Tool result: {entry['result']}")
        elif role in ("assistant", "error"):
            print("Agent decided to answer.")


def main():
    print("Mini Agent - ask a calculation (e.g. 12 * 7) or the time. Type 'quit' to exit.")
    while True:
        try:
            user_input = input("\nUser: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if user_input.lower() in ("quit", "exit"):
            break
        if not user_input:
            continue

        final_answer, history = run_agent(user_input)
        print_history(history)
        print(f"\nFinal answer: {final_answer}")


if __name__ == "__main__":
    main()
