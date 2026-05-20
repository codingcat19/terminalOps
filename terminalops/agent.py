"""Agent construction helpers for TerminalOps."""

from __future__ import annotations

from terminalops.config import (
    DEFAULT_AGENT_NAME,
    DEFAULT_MODEL_HOST,
    DEFAULT_MODEL_ID,
    SYSTEM_PROMPT,
)
from terminalops.tools import build_tools


class MissingDependencyError(RuntimeError):
    """Raised when runtime dependencies are unavailable."""


def create_terminalops_agent(confirm_callback=None):
    """Create a configured Strands agent for TerminalOps."""
    try:
        from strands import Agent
        from strands.models.ollama import OllamaModel
    except ImportError as exc:
        raise MissingDependencyError(
            "TerminalOps requires 'strands-agents[ollama]' to be installed."
        ) from exc

    model = OllamaModel(
        host=DEFAULT_MODEL_HOST,
        model_id=DEFAULT_MODEL_ID,
    )
    tools = build_tools(confirm_callback=confirm_callback)

    agent = Agent(
        model=model,
        name=DEFAULT_AGENT_NAME,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )
    return agent, tools
