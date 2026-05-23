"""Interactive CLI for TerminalOps."""

from __future__ import annotations

import argparse
import contextlib
import io
import sys
from typing import Callable

from terminalops.agent import MissingDependencyError, create_terminalops_agent
from terminalops.config import (
    DEFAULT_MODEL_HOST,
    DEFAULT_MODEL_ID,
    get_model_provider,
)
from terminalops.tools import (
    describe_tools,
    get_docker_containers_text,
    get_docker_images_text,
    get_git_status_text,
    get_system_resources_text,
    get_system_time_text,
)


class TerminalOpsCLI:
    """Interactive REPL for the TerminalOps agent."""

    def __init__(
        self,
        input_func: Callable[[str], str] = input,
        output_func: Callable[[str], None] = print,
    ) -> None:
        self.input_func = input_func
        self.output_func = output_func
        self.agent = None
        self.tools = []
        self.last_direct_intent = None
        self.reset_session()

    def reset_session(self) -> None:
        self.agent, self.tools = create_terminalops_agent(
            confirm_callback=self.confirm_command
        )

    def confirm_command(self, command: str) -> bool:
        self.output_func("")
        self.output_func("Approval needed for a state-changing shell action:")
        self.output_func(f"  {command}")
        while True:
            reply = self.input_func("Run it? [y/N]: ").strip().lower()
            if reply in {"y", "yes"}:
                return True
            if reply in {"", "n", "no"}:
                return False
            self.output_func("Please answer with 'y' or 'n'.")

    def print_banner(self) -> None:
        self.output_func("TerminalOps")
        self.output_func(
            f"Model: {DEFAULT_MODEL_ID} via {get_model_provider().title()} "
            f"at {DEFAULT_MODEL_HOST if get_model_provider() == 'ollama' else 'OpenAI API'}"
        )
        self.output_func("Type /help for commands.")

    def print_help(self) -> None:
        self.output_func("Available commands:")
        self.output_func("  /help   Show CLI commands")
        self.output_func("  /tools  Show built-in tools")
        self.output_func("  /docker Show Docker containers and images")
        self.output_func("  /clear  Reset the current session memory")
        self.output_func("  /status Show model and tool status")
        self.output_func("  /exit   Exit TerminalOps")

    def print_tools(self) -> None:
        self.output_func("Loaded tools:")
        for tool_name in describe_tools(self.tools):
            self.output_func(f"  - {tool_name}")

    def print_status(self) -> None:
        self.output_func("TerminalOps status")
        self.output_func(f"  Model host: {DEFAULT_MODEL_HOST}")
        self.output_func(f"  Model id: {DEFAULT_MODEL_ID}")
        self.output_func(f"  Loaded tools: {len(self.tools)}")

    def handle_command(self, line: str) -> bool:
        command = line.strip()
        if command == "/help":
            self.print_help()
            return True
        if command == "/tools":
            self.print_tools()
            return True
        if command == "/clear":
            self.reset_session()
            self.output_func("Session memory cleared.")
            return True
        if command == "/status":
            self.print_status()
            return True
        if command == "/docker":
            self.print_docker_status()
            return True
        if command == "/exit":
            self.output_func("Bye.")
            return False
        if command.startswith("/"):
            self.output_func(f"Unknown command: {command}")
            self.output_func("Type /help for available commands.")
            return True
        if self.handle_direct_request(command):
            return True
        return self.handle_prompt(command)

    def handle_direct_request(self, prompt: str) -> bool:
        normalized = prompt.strip().lower()
        if not normalized:
            return True

        if self.last_direct_intent == "resources" and normalized in {
            "show it",
            "please show it",
            "show",
            "show me",
            "yes",
        }:
            self.print_resources()
            return True

        if any(term in normalized for term in ("resource", "resources", "cpu", "ram", "memory")):
            self.print_resources()
            return True

        if "time" in normalized or "date" in normalized:
            self.output_func(get_system_time_text())
            self.last_direct_intent = "time"
            return True

        if "git status" in normalized or "current branch" in normalized:
            self.output_func(get_git_status_text())
            self.last_direct_intent = "git"
            return True

        if "docker ps" in normalized or "running containers" in normalized:
            self.output_func(get_docker_containers_text())
            self.last_direct_intent = "docker"
            return True

        if "docker images" in normalized or "list images" in normalized:
            self.output_func(get_docker_images_text())
            self.last_direct_intent = "docker"
            return True

        return False

    def print_resources(self) -> None:
        self.output_func(get_system_resources_text())
        self.last_direct_intent = "resources"

    def print_docker_status(self) -> None:
        self.output_func("Docker Containers:")
        self.output_func(get_docker_containers_text())
        self.output_func("")
        self.output_func("Docker Images:")
        self.output_func(get_docker_images_text())
        self.last_direct_intent = "docker"

    def handle_prompt(self, prompt: str) -> bool:
        if not prompt:
            return True

        try:
            captured_output = io.StringIO()
            with contextlib.redirect_stdout(captured_output):
                response = self.agent(prompt)
        except Exception as exc:  # pragma: no cover - runtime library behavior
            self.output_func(f"Agent error: {exc}")
            return True

        if response is not None:
            self.output_func(str(response))
        return True

    def run(self) -> int:
        self.print_banner()

        while True:
            try:
                line = self.input_func("> ")
            except EOFError:
                self.output_func("")
                self.output_func("Bye.")
                return 0
            except KeyboardInterrupt:
                self.output_func("")
                self.output_func("Interrupted. Use /exit to quit.")
                continue

            if not self.handle_command(line):
                return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="terminalops",
        description="Terminal-first DevOps agent powered by Strands and Ollama.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    parser.parse_args(argv)

    try:
        cli = TerminalOpsCLI()
    except MissingDependencyError as exc:
        print(exc, file=sys.stderr)
        return 1

    return cli.run()


if __name__ == "__main__":
    raise SystemExit(main())
