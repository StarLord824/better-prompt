# ⚡ better-prompt-cli — Modular Prompt Enhancer Command-Line Tool

> A lightweight, extensible CLI framework built for developers who want performance, flexibility, and deep AI integrations — without the complexity.

---

## Constraints:

- Core Constraint: Error-Proof Coder → Program never crashes, handles all inputs
- Line Budget: Detailed Creator → 300 lines maximum
- Project Domain: Text Processing → Editors, analyzers, formatters

## 🚀 Overview

**better-prompt-cli** is a single-file Python command-line tool designed for high extensibility.  
It can run locally, fetch intelligent responses from AI APIs, or interact with plugins stored in external repositories — all in one unified interface.

The project is modular by design, enabling developers to:
- 🧩 **Add or import plugins** from external repos (LangChain, OpenRouter, n8n, etc.)
- ⚙️ **Extend command handlers** dynamically
- 🤖 **Integrate AI models** with custom prompts per model/provider
- 🧠 **Refine prompts** using XML-based self-adjusting logic

---

## 💡 Core Features

| Feature | Description |
|----------|--------------|
| **🪶 Lightweight Single File** | Simple architecture — no frameworks, just Python. |
| **🔌 Plugin System (Planned)** | Extend the CLI with public or private modules. |
| **🧠 AI-Powered Commands** | Integrate with GPT, Claude, Gemini, or custom models. |
| **⚙️ Smart Prompt Selection** | Uses pre-mapped best prompt structures per model. |
| **🔍 Configurable via JSON/YAML** | Local config file for runtime overrides. |
| **🚀 Deploy Anywhere** | Works on any environment with Python 3.8+. |

---

## 🛠️ Installation

You can install directly from **PyPI** once published:

```bash
pip install better-prompt-cli
```

## 🧩 Usage

```Basic command:
better-prompt-cli run
```

## Pass arguments or model preferences:

```better-prompt-cli run --model claude-3 --prompt "Generate CI/CD workflow"```


###  For debugging:
```
better-prompt-cli debug --verbose
```

## 🧠 How It Works

- Command Parsing:
The CLI reads the user command (run, debug, etc.) and parses arguments.

- Prompt Mapping:
A table of model-specific prompt structures ensures optimal formatting for each LLM.

- AI Invocation:
Depending on config, the CLI calls the chosen API (OpenAI, Anthropic, etc.).

- Dynamic Adjustments:
If AI responses suggest code changes, the CLI intelligently modifies or re-executes parts of the logic.

- Plugin Bootstrapping (Future):
Once plugin support is enabled, the CLI fetches and loads public plugin modules dynamically.

## 🧪 Development

### Clone and install in editable mode:
```
git clone https://github.com/StarLord824//better-prompt.git
cd better-prompt
pip install -e .
```

### Run locally:
```
python better-prompt-cli.py
```
