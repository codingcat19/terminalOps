import unittest
from unittest.mock import patch

from terminalops.tools import build_tools, get_system_resources_text


class ToolTests(unittest.TestCase):
    def test_read_only_shell_command_runs_without_confirmation(self):
        tools = build_tools(confirm_callback=lambda command: False)
        shell_command = next(tool for tool in tools if tool.__name__ == "shell_command")

        with patch("terminalops.tools._run_command", return_value="ok") as run_command:
            result = shell_command("git status -s -b")

        self.assertEqual(result, "ok")
        run_command.assert_called_once_with("git status -s -b")

    def test_risky_shell_command_is_blocked_when_not_approved(self):
        tools = build_tools(confirm_callback=lambda command: False)
        shell_command = next(tool for tool in tools if tool.__name__ == "shell_command")

        with patch("terminalops.tools._run_command") as run_command:
            result = shell_command("git commit -m 'test'")

        self.assertIn("not approved", result)
        run_command.assert_not_called()

    def test_system_resources_include_concrete_values(self):
        with patch("terminalops.tools.psutil") as psutil:
            psutil.cpu_percent.return_value = 12.5
            psutil.virtual_memory.return_value.percent = 40
            psutil.virtual_memory.return_value.used = 4 * 1024 * 1024 * 1024
            psutil.virtual_memory.return_value.total = 8 * 1024 * 1024 * 1024
            psutil.disk_usage.return_value.percent = 55
            psutil.disk_usage.return_value.used = 55 * 1024 * 1024 * 1024
            psutil.disk_usage.return_value.total = 100 * 1024 * 1024 * 1024

            result = get_system_resources_text()

        self.assertIn("CPU Usage: 12.5%", result)
        self.assertIn("RAM Usage: 40%", result)
        self.assertIn("Disk Usage: 55%", result)

    def test_docker_images_tool_runs(self):
        tools = build_tools(confirm_callback=lambda command: False)
        list_images = next(tool for tool in tools if tool.__name__ == "list_images")

        with patch("terminalops.tools._run_command", return_value="IMAGE LIST") as run_command:
            result = list_images()

        self.assertEqual(result, "IMAGE LIST")
        run_command.assert_called_once_with("docker images")


if __name__ == "__main__":
    unittest.main()
