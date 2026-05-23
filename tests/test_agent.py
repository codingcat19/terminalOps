import os
import unittest
from unittest.mock import Mock, patch

from terminalops.agent import MissingDependencyError, create_terminalops_agent


class FakeAgent:
    def __init__(self, model, name, tools, system_prompt):
        self.model = model
        self.name = name
        self.tools = tools
        self.system_prompt = system_prompt


class FakeOllamaModel:
    def __init__(self, host=None, model_id=None):
        self.host = host
        self.model_id = model_id


class FakeOpenAIModel:
    def __init__(self, api_key=None, model_id=None, api_base=None):
        self.api_key = api_key
        self.model_id = model_id
        self.api_base = api_base


class AgentProviderTests(unittest.TestCase):
    def setUp(self):
        self.fake_strands = Mock()
        self.fake_strands.Agent = FakeAgent
        self.fake_ollama_module = Mock()
        self.fake_ollama_module.OllamaModel = FakeOllamaModel
        self.fake_openai_module = Mock()
        self.fake_openai_module.OpenAIModel = FakeOpenAIModel

    def import_side_effect(self, name):
        if name == "strands":
            return self.fake_strands
        if name == "strands.models.ollama":
            return self.fake_ollama_module
        if name == "strands.models.openai":
            return self.fake_openai_module
        raise ImportError(f"No module named {name}")

    @patch("terminalops.agent._import_module")
    def test_default_provider_uses_ollama(self, import_module):
        import_module.side_effect = self.import_side_effect

        with patch.dict(os.environ, {"TERMINALOPS_MODEL_PROVIDER": "ollama"}):
            agent, tools = create_terminalops_agent(confirm_callback=lambda command: True)

        self.assertIsInstance(agent, FakeAgent)
        self.assertIsInstance(agent.model, FakeOllamaModel)
        self.assertEqual(agent.model.host, "http://localhost:11434")
        self.assertEqual(agent.model.model_id, "llama3.2")

    @patch("terminalops.agent._import_module")
    def test_openai_provider_requires_api_key(self, import_module):
        import_module.side_effect = self.import_side_effect

        with patch.dict(os.environ, {"TERMINALOPS_MODEL_PROVIDER": "openai"}, clear=True):
            with self.assertRaises(MissingDependencyError) as context:
                create_terminalops_agent(confirm_callback=lambda command: True)

        self.assertIn("TERMINALOPS_OPENAI_API_KEY", str(context.exception))

    @patch("terminalops.agent._import_module")
    def test_openai_provider_uses_openai_model(self, import_module):
        import_module.side_effect = self.import_side_effect

        env = {
            "TERMINALOPS_MODEL_PROVIDER": "openai",
            "TERMINALOPS_OPENAI_API_KEY": "test-key",
            "TERMINALOPS_OPENAI_MODEL_ID": "gpt-3.5-turbo",
            "TERMINALOPS_OPENAI_API_BASE": "https://api.openai.com/v1",
        }

        with patch.dict(os.environ, env, clear=True):
            agent, tools = create_terminalops_agent(confirm_callback=lambda command: True)

        self.assertIsInstance(agent, FakeAgent)
        self.assertIsInstance(agent.model, FakeOpenAIModel)
        self.assertEqual(agent.model.api_key, "test-key")
        self.assertEqual(agent.model.model_id, "gpt-3.5-turbo")
        self.assertEqual(agent.model.api_base, "https://api.openai.com/v1")

    @patch("terminalops.agent._import_module")
    def test_unknown_provider_raises_value_error(self, import_module):
        import_module.side_effect = self.import_side_effect

        with patch.dict(os.environ, {"TERMINALOPS_MODEL_PROVIDER": "unknown"}, clear=True):
            with self.assertRaises(ValueError):
                create_terminalops_agent(confirm_callback=lambda command: True)


if __name__ == "__main__":
    unittest.main()
