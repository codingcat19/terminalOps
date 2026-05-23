"""Shared configuration for TerminalOps."""

import os

DEFAULT_MODEL_PROVIDER = "ollama"
DEFAULT_MODEL_HOST = "http://localhost:11434"
DEFAULT_MODEL_ID = "llama3.2"
DEFAULT_OPENAI_MODEL_ID = "gpt-3.5-turbo"
DEFAULT_AGENT_NAME = "TerminalOps"

SYSTEM_PROMPT = """You are TerminalOps, a senior DevOps terminal assistant.
Use the provided tools whenever they are relevant.

Guidelines:
- Prefer specialized tools for Docker, git status, system time, and system resources.
- Use shell_command for general terminal, file system, git, and DevOps tasks.
- Before destructive shell actions, the CLI may ask for confirmation.
- If a command fails, explain the failure clearly and suggest the next useful step.
- Keep responses concise and practical for terminal use.
"""


def get_model_provider() -> str:
    return os.environ.get("TERMINALOPS_MODEL_PROVIDER", DEFAULT_MODEL_PROVIDER).strip().lower()


def get_openai_api_key() -> str:
    return os.environ.get("TERMINALOPS_OPENAI_API_KEY", "").strip()


def get_openai_model_id() -> str:
    return os.environ.get("TERMINALOPS_OPENAI_MODEL_ID", DEFAULT_OPENAI_MODEL_ID).strip()


def get_openai_api_base() -> str:
    return os.environ.get("TERMINALOPS_OPENAI_API_BASE", "").strip()
