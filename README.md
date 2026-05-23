# TerminalOps

TerminalOps is a terminal-first DevOps agent built with [Strands](https://github.com/strands-agents/sdk-python). It supports local LLM execution via **Ollama** (default) and optional **OpenAI** integration.

## Features

- Interactive CLI REPL with `/help`, `/tools`, `/docker`, `/files`, `/clear`, `/status`, and `/exit` commands
- Shell safety layer — read-only commands run directly, state-changing commands require approval
- Built-in tools for Docker, Git, system resources, file browsing, and code search
- Streamlit web UI via `app.py`
- Pluggable model provider: Ollama (local) or OpenAI

## Install

```bash
python3.12 -m venv .venv312
source .venv312/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Configuration

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Then edit `.env`:

```env
# Use "ollama" (default) or "openai"
TERMINALOPS_MODEL_PROVIDER=openai

TERMINALOPS_OPENAI_API_KEY=your_openai_api_key_here
TERMINALOPS_OPENAI_MODEL_ID=gpt-3.5-turbo

# Optional: leave blank to use the default OpenAI API endpoint
TERMINALOPS_OPENAI_API_BASE=
```

> Note: When using Ollama, no API key is needed. Make sure Ollama is running locally at `http://localhost:11434` with the `llama3.2` model pulled.

### Optional OpenAI install extras

```bash
pip install -e .[openai]
```

> Note: OpenAI typically offers a free trial or limited credits for new accounts, but ongoing usage is billed per request.

## Run

**Interactive CLI:**
```bash
terminalops
```

**Streamlit Web UI:**
```bash
streamlit run app.py
```

## Tests

```bash
.venv312/bin/python -m unittest discover -s tests -v
```
