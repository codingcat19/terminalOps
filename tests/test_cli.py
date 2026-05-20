import unittest
from unittest.mock import patch

from terminalops.agent import MissingDependencyError
from terminalops.cli import TerminalOpsCLI, main


class FakeAgent:
    def __init__(self):
        self.prompts = []

    def __call__(self, prompt):
        self.prompts.append(prompt)
        return f"handled: {prompt}"


class TerminalOpsCLITests(unittest.TestCase):
    def test_help_command_prints_usage(self):
        outputs = []
        fake_agent = FakeAgent()

        with patch("terminalops.cli.create_terminalops_agent", return_value=(fake_agent, [])):
            cli = TerminalOpsCLI(
                input_func=lambda prompt: "",
                output_func=outputs.append,
            )

        cli.handle_command("/help")

        self.assertTrue(any("/help" in line for line in outputs))
        self.assertTrue(any("/exit" in line for line in outputs))

    def test_clear_command_recreates_agent(self):
        outputs = []
        first_agent = FakeAgent()
        second_agent = FakeAgent()

        with patch(
            "terminalops.cli.create_terminalops_agent",
            side_effect=[(first_agent, []), (second_agent, [])],
        ):
            cli = TerminalOpsCLI(
                input_func=lambda prompt: "",
                output_func=outputs.append,
            )
            cli.handle_command("/clear")

        self.assertIs(cli.agent, second_agent)
        self.assertIn("Session memory cleared.", outputs)

    def test_prompt_is_sent_to_agent(self):
        outputs = []
        fake_agent = FakeAgent()

        with patch("terminalops.cli.create_terminalops_agent", return_value=(fake_agent, [])):
            cli = TerminalOpsCLI(
                input_func=lambda prompt: "",
                output_func=outputs.append,
            )

        cli.handle_command("check docker status")

        self.assertEqual(fake_agent.prompts, ["check docker status"])
        self.assertIn("handled: check docker status", outputs)

    def test_system_resources_are_handled_directly(self):
        outputs = []
        fake_agent = FakeAgent()

        with patch("terminalops.cli.create_terminalops_agent", return_value=(fake_agent, [])):
            cli = TerminalOpsCLI(
                input_func=lambda prompt: "",
                output_func=outputs.append,
            )

        with patch("terminalops.cli.get_system_resources_text", return_value="CPU Usage: 10%"):
            cli.handle_command("check system resources")

        self.assertEqual(fake_agent.prompts, [])
        self.assertIn("CPU Usage: 10%", outputs)

    def test_show_it_repeats_last_resource_check(self):
        outputs = []
        fake_agent = FakeAgent()

        with patch("terminalops.cli.create_terminalops_agent", return_value=(fake_agent, [])):
            cli = TerminalOpsCLI(
                input_func=lambda prompt: "",
                output_func=outputs.append,
            )

        with patch("terminalops.cli.get_system_resources_text", return_value="RAM Usage: 20%"):
            cli.handle_command("check system resources")
            cli.handle_command("Please show it")

        self.assertEqual(outputs.count("RAM Usage: 20%"), 2)

    def test_main_returns_error_when_dependencies_are_missing(self):
        with patch(
            "terminalops.cli.TerminalOpsCLI",
            side_effect=MissingDependencyError("missing deps"),
        ):
            self.assertEqual(main([]), 1)


if __name__ == "__main__":
    unittest.main()
