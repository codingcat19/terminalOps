# TerminalOps

TerminalOps is a terminal-first DevOps agent built with Strands and Ollama.

## Install

```bash
python3.12 -m venv .venv312
source .venv312/bin/activate
pip install -r requirements.txt
pip install -e .
```

### Optional OpenAI support

If you want to use OpenAI instead of Ollama, install the optional package extras:

```bash
pip install -e .[openai]
```

Then set the provider and API key:

```bash
export TERMINALOPS_MODEL_PROVIDER=openai
export TERMINALOPS_OPENAI_API_KEY="your_openai_api_key"
export TERMINALOPS_OPENAI_MODEL_ID="gpt-3.5-turbo"
```

> Note: OpenAI typically offers a free trial or limited credits for new accounts, but ongoing usage is billed per request.

## Run

```bash
terminalops
```
