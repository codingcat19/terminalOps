from terminalops.agent import MissingDependencyError, create_terminalops_agent


def run_docker_check():
    print("--- Docker Monitoring Agent Online ---")

    try:
        docker_agent, _ = create_terminalops_agent(confirm_callback=lambda command: True)
    except MissingDependencyError as exc:
        print(exc)
        return

    query = input(
        "Enter your task (e.g., 'List containers' or 'Show logs for xyz container'): "
    )

    response = docker_agent(query)

    print("\n--- FINAL AGENT RESPONSE ---")
    print(response)


if __name__ == "__main__":
    run_docker_check()
