import unittest

from terminalops.safety import is_read_only_command, needs_confirmation


class SafetyTests(unittest.TestCase):
    def test_read_only_command_does_not_need_confirmation(self):
        self.assertTrue(is_read_only_command("git status -s -b"))
        self.assertFalse(needs_confirmation("git status -s -b"))

    def test_state_changing_command_needs_confirmation(self):
        self.assertTrue(needs_confirmation("git commit -m 'test'"))

    def test_compound_command_needs_confirmation(self):
        self.assertTrue(needs_confirmation("ls && rm -rf tmp"))


if __name__ == "__main__":
    unittest.main()
