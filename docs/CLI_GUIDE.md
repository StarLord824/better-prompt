# Better Prompt CLI - User Guide

## 🚀 Installation

### Install from source

```bash
cd better-prompt
pip install -e .
```

This will install the `better-prompt` command globally.

### Verify installation

```bash
better-prompt --help
```

---

## 📖 Commands

### 1. **process** - Process a single prompt

Process and optimize a prompt for a specific model.

#### Basic Usage

```bash
# Interactive mode (will prompt for input)
better-prompt process

# Direct prompt
better-prompt process "Write a Python function to sort an array"

# With model specification
better-prompt process "Create an image" -m gpt-4 -p OpenAI

# With tone
better-prompt process "Explain quantum computing" -t casual

# Save to file
better-prompt process "Debug this code" -o output.txt
```

#### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--model` | `-m` | Target model (e.g., gpt-4, claude-3-opus) | None |
| `--provider` | `-p` | Model provider (e.g., OpenAI, Anthropic) | None |
| `--tone` | `-t` | Tone: professional, casual, technical, creative, formal, friendly, neutral | professional |
| `--format` | `-f` | Output format: json, xml, yaml, markdown, text | Auto-detected |
| `--no-template` | | Don't apply format template | False |
| `--output` | `-o` | Save refined prompt to file | None |
| `--verbose` | `-v` | Show detailed information | False |

#### Examples

```bash
# Professional tone for GPT-4
better-prompt process "Write API documentation" -m gpt-4 -p OpenAI -t professional

# Casual tone for Claude
better-prompt process "Explain machine learning" -m claude-3-opus -p Anthropic -t casual

# Technical tone with JSON format
better-prompt process "Create a REST API" -t technical -f json

# Save output to file
better-prompt process "Generate test cases" -m gpt-4 -p OpenAI -o refined.txt -v
```

---

### 2. **batch** - Process multiple prompts

Process multiple prompts from a JSON file.

#### Input File Format

Create a JSON file (e.g., `prompts.json`):

```json
{
  "prompts": [
    "Write a Python function to validate emails",
    "Create an image of a sunset",
    "Translate this to Spanish",
    "Debug my React component",
    "Summarize this article"
  ]
}
```

#### Usage

```bash
# Basic batch processing
better-prompt batch prompts.json

# With model specification
better-prompt batch prompts.json -m gpt-4 -p OpenAI

# Save results to file
better-prompt batch prompts.json -m gpt-4 -p OpenAI -o results.json
```

#### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--model` | `-m` | Target model for all prompts |
| `--provider` | `-p` | Model provider for all prompts |
| `--output` | `-o` | Save results to JSON file |

#### Output Format

When using `-o`, the output JSON contains:

```json
{
  "statistics": {
    "total_prompts": 5,
    "task_type_distribution": {
      "code_generation": 2,
      "image_generation": 1,
      "translation": 1,
      "code_debug": 1
    },
    "format_distribution": {
      "markdown": 5
    },
    "average_task_confidence": 0.85,
    "average_format_confidence": 1.0,
    "total_improvements": 15
  },
  "results": [
    {
      "original": "Write a Python function...",
      "refined": "Please write a Python function...",
      "task_type": "code_generation",
      "confidence": 1.0,
      "format": "markdown"
    }
  ]
}
```

---

### 3. **classify** - Classify a prompt

Identify the task type of a prompt without full processing.

#### Usage

```bash
better-prompt classify "Write a Python function"
better-prompt classify "Create an image of a sunset"
better-prompt classify "Translate to French"
```

#### Output

```
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Property  ┃ Value                                               ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Task Type │ code_generation                                     │
│ Confidence│ 100%                                                │
│ Reasoning │ Classified as code_generation based on heuristic... │
└───────────┴─────────────────────────────────────────────────────┘
```

---

### 4. **models** - List supported models

View all supported models and their preferred formats.

#### Usage

```bash
# List all models
better-prompt models

# Filter by provider
better-prompt models --provider OpenAI
better-prompt models -p Anthropic

# Filter by format
better-prompt models --format json
better-prompt models -f xml
```

#### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--provider` | `-p` | Filter by provider |
| `--format` | `-f` | Filter by preferred format |

#### Output

```
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Provider  ┃ Model               ┃ Preferred Format ┃
━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ OpenAI    │ gpt-4               │ markdown         │
│ OpenAI    │ gpt-4o              │ markdown         │
│ OpenAI    │ o1-research         │ json             │
│ Anthropic │ claude-3-opus       │ xml              │
│ Google    │ gemini-pro          │ json             │
└───────────┴─────────────────────┴──────────────────┘

Total: 37 models
```

---

### 5. **info** - System information

Display Better Prompt system information.

#### Usage

```bash
better-prompt info
```

#### Output

```
ℹ️  Better Prompt - System Information

Version          0.1.0
Task Types       15+
Supported Models 37+
Output Formats   5
Tone Options     7

Available Components:
  ✓ Task Classifier
  ✓ Format Selector
  ✓ Refinement Pipeline
  ✓ Pipeline Orchestrator
  ✓ Plugin System
  ✓ LLM Gateway
```

---

## 🎨 Interactive Mode

When you run `better-prompt process` without arguments, it enters interactive mode:

```bash
$ better-prompt process

🚀 Better Prompt - Prompt Optimizer

Enter your prompt: Write a Python function to sort an array
Would you like to specify a target model? [Y/n]: y

Select Provider:
  1. OpenAI
  2. Anthropic
  3. Google
  4. Alibaba
  5. DeepSeek
  6. xAI
Enter number [1]: 1

Select OpenAI Model:
  1. gpt-4
  2. gpt-4o
  3. gpt-4o-mini
  4. o1-research
Enter number [1]: 1

Processing prompt... ✓

[Results displayed...]
```

---

## 🎯 Common Workflows

### Workflow 1: Quick Prompt Improvement

```bash
# Quick improvement with defaults
better-prompt process "write code to validate emails"
```

### Workflow 2: Model-Specific Optimization

```bash
# Optimize for specific model
better-prompt process "Create an API" -m gpt-4 -p OpenAI -t professional -v
```

### Workflow 3: Batch Processing

```bash
# 1. Create prompts.json
echo '{
  "prompts": [
    "Write a Python function",
    "Create an image",
    "Debug this code"
  ]
}' > prompts.json

# 2. Process batch
better-prompt batch prompts.json -m gpt-4 -p OpenAI -o results.json

# 3. View results
cat results.json
```

### Workflow 4: Task Analysis

```bash
# Analyze what type of task your prompt is
better-prompt classify "Build a REST API with authentication"
```

### Workflow 5: Model Discovery

```bash
# Find all models that prefer JSON
better-prompt models --format json

# Find all Anthropic models
better-prompt models --provider Anthropic
```

---

## 📝 Tips & Best Practices

### 1. **Use Verbose Mode for Learning**

```bash
better-prompt process "Your prompt" -v
```

This shows detailed information about the processing stages.

### 2. **Save Refined Prompts**

```bash
better-prompt process "Your prompt" -o refined.txt
```

Build a library of optimized prompts.

### 3. **Batch Process Similar Prompts**

Group similar prompts in a JSON file and process them together for consistency.

### 4. **Experiment with Tones**

```bash
# Try different tones to see what works best
better-prompt process "Explain AI" -t casual
better-prompt process "Explain AI" -t technical
better-prompt process "Explain AI" -t formal
```

### 5. **Use Model-Specific Optimization**

Always specify the target model for best results:

```bash
better-prompt process "Your prompt" -m gpt-4 -p OpenAI
```

---

## 🔧 Troubleshooting

### Command not found

If `better-prompt` command is not found:

```bash
# Reinstall in editable mode
pip install -e .

# Or use python -m
python -m better_prompt.cli.main process "Your prompt"
```

### Import errors

Make sure all dependencies are installed:

```bash
pip install -r requirements.txt
```

### Permission errors

On Unix systems, you might need:

```bash
chmod +x $(which better-prompt)
```

---

## 🚀 Advanced Usage

### Piping Output

```bash
# Pipe refined prompt to clipboard (macOS)
better-prompt process "Your prompt" | pbcopy

# Pipe to file
better-prompt process "Your prompt" > refined.txt

# Chain with other commands
better-prompt process "Your prompt" | wc -l
```

### Environment Variables

You can set default values:

```bash
export BETTER_PROMPT_MODEL="gpt-4"
export BETTER_PROMPT_PROVIDER="OpenAI"
export BETTER_PROMPT_TONE="professional"
```

### Scripting

Use in shell scripts:

```bash
#!/bin/bash

# Process multiple prompts
for prompt in "Prompt 1" "Prompt 2" "Prompt 3"; do
    better-prompt process "$prompt" -m gpt-4 -p OpenAI -o "output_${i}.txt"
    ((i++))
done
```

---

## 📚 Examples Library

### Code Generation

```bash
better-prompt process "Write a Python function to validate email addresses using regex" \
  -m gpt-4 -p OpenAI -t professional -o email_validator.txt
```

### Image Generation

```bash
better-prompt process "Create a photorealistic image of a sunset over mountains" \
  -m gpt-4 -p OpenAI -t creative
```

### Data Analysis

```bash
better-prompt process "Analyze this sales data and find trends" \
  -m gemini-pro -p Google -t technical -f json
```

### Documentation

```bash
better-prompt process "Write API documentation for a REST endpoint" \
  -m gpt-4 -p OpenAI -t professional -f markdown
```

---

## 🎓 Next Steps

1. **Try the examples** above
2. **Experiment with different tones** and models
3. **Build your prompt library** using batch processing
4. **Integrate into your workflow** using scripts

For more information, see:
- [README.md](../README.md) - Full documentation
- [QUICKSTART.md](../QUICKSTART.md) - Quick start guide
- [FAQ.md](../FAQ.md) - Frequently asked questions

---

**Better Prompt CLI** - Transform your prompts from the command line! 🚀
