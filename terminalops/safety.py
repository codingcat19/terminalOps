"""Safety heuristics for shell execution."""

from __future__ import annotations

import re
import shlex


READ_ONLY_PREFIXES = (
    ("pwd",),
    ("ls",),
    ("cat",),
    ("head",),
    ("tail",),
    ("grep",),
    ("rg",),
    ("find",),
    ("which",),
    ("whoami",),
    ("uname",),
    ("date",),
    ("ps",),
    ("top",),
    ("df",),
    ("du",),
    ("env",),
    ("printenv",),
    ("git", "status"),
    ("git", "branch"),
    ("git", "log"),
    ("git", "diff"),
    ("git", "show"),
    ("docker", "ps"),
    ("docker", "images"),
    ("docker", "logs"),
    ("docker", "inspect"),
    ("kubectl", "get"),
    ("kubectl", "describe"),
    ("kubectl", "logs"),
)

RISKY_TOKENS = {
    "rm",
    "mv",
    "cp",
    "chmod",
    "chown",
    "sudo",
    "tee",
    "sed",
    "awk",
}

RISKY_SUBCOMMANDS = {
    ("git", "add"),
    ("git", "commit"),
    ("git", "switch"),
    ("git", "checkout"),
    ("git", "merge"),
    ("git", "rebase"),
    ("git", "reset"),
    ("git", "clean"),
    ("docker", "run"),
    ("docker", "stop"),
    ("docker", "start"),
    ("docker", "restart"),
    ("docker", "exec"),
    ("docker", "rm"),
    ("docker", "rmi"),
    ("docker", "compose"),
    ("kubectl", "apply"),
    ("kubectl", "delete"),
    ("kubectl", "edit"),
    ("kubectl", "exec"),
}

COMPOUND_PATTERN = re.compile(r"[;&|]|&&|\|\|")
WRITE_REDIRECT_PATTERN = re.compile(r">")


def is_read_only_command(command: str) -> bool:
    """Return True when the command looks safe to run without confirmation."""
    if not command or not command.strip():
        return False

    stripped = command.strip()
    if COMPOUND_PATTERN.search(stripped) or WRITE_REDIRECT_PATTERN.search(stripped):
        return False
    
    # Check for command substitution which can lead to injection
    if '$(' in stripped or '`' in stripped:
        return False

    try:
        parts = shlex.split(stripped)
    except ValueError:
        return False

    if not parts:
        return False

    lowered = tuple(part.lower() for part in parts[:2])

    if parts[0].lower() in RISKY_TOKENS:
        return False

    if lowered in RISKY_SUBCOMMANDS:
        return False

    for prefix in READ_ONLY_PREFIXES:
        if tuple(part.lower() for part in parts[: len(prefix)]) == prefix:
            return True

    return False


def needs_confirmation(command: str) -> bool:
    """Return True when the CLI should confirm shell execution."""
    return not is_read_only_command(command)
