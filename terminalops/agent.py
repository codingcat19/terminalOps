"""Agent construction helpers for TerminalOps."""

from __future__ import annotations

import importlib
from typing import Any

from terminalops.config import (
    DEFAULT_AGENT_NAME,
    DEFAULT_MODEL_HOST,
    DEFAULT_MODEL_ID,
    SYSTEM_PROMPT,
    get_model_provider,
    get_openai_api_base,
    get_openai_api_key,
    get_openai_model_id,
)
from terminalops.tools import build_tools


class MissingDependencyError(RuntimeError):
    """Raised when runtime dependencies are unavailable."""


def _import_module(name: str) -> Any:
    return importlib.import_module(name)


def create_terminalops_agent(confirm_callback=None):
    """Create a configured Strands agent for TerminalOps."""
    try:
        strands = _import_module("strands")
        Agent = strands.Agent
    except ImportError as exc:
        raise MissingDependencyError(
            "TerminalOps requires the 'strands' package to be installed."
        ) from exc

    provider = get_model_provider()
    if provider == "ollama":
        try:
            OllamaModel = _import_module("strands.models.ollama").OllamaModel
        except (ImportError, AttributeError) as exc:
            raise MissingDependencyError(
                "TerminalOps requires 'strands-agents[ollama]' to be installed for the Ollama provider."
            ) from exc

        model = OllamaModel(
            host=DEFAULT_MODEL_HOST,
            model_id=DEFAULT_MODEL_ID,
        )
    elif provider == "openai":
        try:
            OpenAIModel = _import_module("strands.models.openai").OpenAIModel
        except (ImportError, AttributeError) as exc:
            raise MissingDependencyError(
                "TerminalOps requires 'strands-agents[openai]' to be installed for the OpenAI provider."
            ) from exc

        api_key = get_openai_api_key()
        if not api_key:
            raise MissingDependencyError(
                "OpenAI provider requires TERMINALOPS_OPENAI_API_KEY to be set."
            )

        model = OpenAIModel(
            api_key=api_key,
            model_id=get_openai_model_id(),
            api_base=get_openai_api_base() or None,
        )
    else:
        raise ValueError(
            f"Unsupported model provider: {provider}. "
            "Supported providers are 'ollama' and 'openai'."
        )

    tools = build_tools(confirm_callback=confirm_callback)

    agent = Agent(
        model=model,
        name=DEFAULT_AGENT_NAME,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )
    return agent, tools
