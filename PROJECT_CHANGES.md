# Project Changes

This file tracks meaningful changes made to the `my-agent` project so future work has a quick memory of what changed and why.

## 2026-05-13

### Git setup

- Initialized `/Users/sahil/Code/DevOps/my-agent` as its own Git repository.
- Created and switched to the feature branch `codex/devops-cli-agent`.
- Left the nested `getting-started-app` Git repository unchanged.

### TerminalOps CLI agent

- Added the `TerminalOps` terminal agent as a new installable CLI command named `terminalops`.
- Added a reusable Python package under `terminalops/` for shared agent setup, tools, safety checks, and CLI behavior.
- Added an interactive REPL with `/help`, `/tools`, `/clear`, `/status`, and `/exit`.
- Added a shell safety layer that allows obvious read-only commands directly and asks for approval before risky or state-changing commands.
- Added reusable tools for shell commands, Docker container operations, git status, system time, and system resources.
- Refactored `app.py`, `docker-agent.py`, and `my_first_agent.py` to reuse the shared `terminalops` agent setup.
- Added `setup.py` and `bin/terminalops` so the project can expose a local CLI command.
- Added `requirements.txt` with the Python runtime dependencies needed by the CLI and Streamlit app.
- Updated project setup docs and metadata to require Python 3.10+ because Strands packages do not install on Python 3.9.
- Added `.gitignore` entries for virtual environments, Python caches, and generated package metadata.
- Added unit tests for CLI command handling, shell safety heuristics, and tool approval behavior.
- Verified the current tests with `.venv/bin/python -m unittest discover -s tests -v`.
- Created a Python 3.12 virtual environment at `.venv312/`, installed dependencies, and verified `terminalops` starts, loads 8 tools, connects to local Ollama, and answers a time prompt through `get_system_time`.
- Fixed the CLI resource-check flow so prompts like `check system resources` and follow-ups like `Please show it` return concrete local CPU, RAM, and disk usage directly instead of generic Linux command suggestions.
- Added richer Docker support with a new `/docker` CLI command, Docker image listing, container inspection, and container exec tooling.
- Added repository browsing support with `/files` and new code-aware tools for listing files and searching source code.
- Added pluggable model provider support for TerminalOps, with Ollama as the default and optional OpenAI support via `TERMINALOPS_MODEL_PROVIDER=openai`.
- Updated docs to explain OpenAI environment variables and optional install extras.
- Suppressed raw Strands tool-trace output for model-handled prompts so the terminal output stays cleaner.

### Known follow-up

- The current virtual environment is missing runtime dependencies such as Strands/Ollama tooling, so the live `terminalops` REPL still needs dependency installation before full end-to-end use.
- Generated install metadata such as `terminalops.egg-info/` should be ignored or cleaned before the first commit.
