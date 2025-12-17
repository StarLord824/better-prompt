# Better Prompt CLI - Quick Reference

## 🚀 Installation

```bash
pip install -e .
```

## 📝 Commands

### Process a Prompt

```bash
# Interactive mode
python -m better_prompt.cli.main process

# Direct
python -m better_prompt.cli.main process "Your prompt here"

# With options
python -m better_prompt.cli.main process "Your prompt" -m gpt-4 -p OpenAI -t professional -o output.txt
```

### Batch Process

```bash
python -m better_prompt.cli.main batch prompts.json -m gpt-4 -p OpenAI -o results.json
```

### Classify Task

```bash
python -m better_prompt.cli.main classify "Your prompt"
```

### List Models

```bash
python -m better_prompt.cli.main models
python -m better_prompt.cli.main models --provider OpenAI
python -m better_prompt.cli.main models --format json
```

### System Info

```bash
python -m better_prompt.cli.main info
```

## 🎨 Options

| Option | Description | Values |
|--------|-------------|--------|
| `-m, --model` | Target model | gpt-4, claude-3-opus, etc. |
| `-p, --provider` | Provider | OpenAI, Anthropic, Google, etc. |
| `-t, --tone` | Tone | professional, casual, technical, creative, formal, friendly, neutral |
| `-f, --format` | Format | json, xml, yaml, markdown, text |
| `-o, --output` | Output file | Path to save file |
| `-v, --verbose` | Verbose mode | Flag |

## 📋 Supported Providers

- **OpenAI**: gpt-4, gpt-4o, gpt-4o-mini, o1-research
- **Anthropic**: claude-3-opus, claude-3-sonnet, claude-4-opus, claude-4-haiku
- **Google**: gemini-pro, gemini-ultra, gemini-1.5-viz, palm-2-enterprise
- **Alibaba**: qwen3-max, qwen2.5-coder-32B, qwen3-omni, qwen2.5-vl
- **DeepSeek**: deepseek-v3.1, deepseek-r1-instruct, deepseek-v2-lite, deepseek-v3-coder
- **xAI**: grok-4, grok-code-fast, grok-vision-2, grok-agent-alpha

## 🎯 Quick Examples

```bash
# Code generation
python -m better_prompt.cli.main process "Write a Python function" -m gpt-4 -p OpenAI

# Image generation
python -m better_prompt.cli.main process "Create an image" -t creative

# Technical writing
python -m better_prompt.cli.main process "Write API docs" -t technical -f markdown

# Batch processing
echo '{"prompts": ["Prompt 1", "Prompt 2"]}' > prompts.json
python -m better_prompt.cli.main batch prompts.json -o results.json
```

## 📖 Full Documentation

See [CLI_GUIDE.md](CLI_GUIDE.md) for complete documentation.
