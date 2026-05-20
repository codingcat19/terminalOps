from terminalops.agent import MissingDependencyError, create_terminalops_agent


def run_sync_test():
    print("--- Attempting Synchronous Call ---")

    try:
        devops_agent, _ = create_terminalops_agent(confirm_callback=lambda command: True)
    except MissingDependencyError as exc:
        print(exc)
        return

    try:
        result = devops_agent("List files in the current directory.")
        print("\n--- AGENT OUTPUT ---")
        print(result)
    except Exception as exc:
        print(f"Sync call failed: {exc}")


if __name__ == "__main__":
    run_sync_test()
