#!/usr/bin/env python3
"""
better_prompt_cli.py - Interactive AI Prompt Refinement Tool

A beautiful CLI tool for refining and optimizing prompts for different AI models.
Supports multiple providers, interactive selection, and plugin system.

Installation:
    pip install rich click aiohttp

Usage:
    python better_prompt_cli.py
"""


"""
Example Run Output:
===================

$ python better_prompt_cli.py

[ASCII LOGO appears]

Step 1: Enter your prompt
> Write a Python function to calculate factorial with error handling

Step 2: Select AI Provider
[Table showing: OpenAI, Anthropic, Google, Alibaba, DeepSeek, xAI]
Choose provider: 2 (Anthropic)

Step 3: Select Model from Anthropic
[Table showing: claude-3-opus, claude-3-sonnet, claude-3-haiku, claude-4-opus]
Choose model: 1 (claude-3-opus)

Step 4: Select Plugin (Optional)
[Table showing plugins]
Choose plugin: 1 (DirectFormatter)

[Spinner: "Refining your prompt..."]

✓ Prompt Optimized Successfully!
Provider: Anthropic
Model: claude-3-opus
Format: XML

Refined Prompt:
[Syntax-highlighted XML output with line numbers]

Save to file? (y/n): n

Refine another prompt? (y/n): n

Thank you for using Better Prompt CLI! 🚀
"""

better_auth.py
│
├── 1️⃣ Imports & Constants (≈ 10–15 lines)
│     └── sys, json, re, textwrap, optional: yaml, xml.etree.ElementTree
│
├── 2️⃣ Utility: Safe Input & Output (≈ 20 lines)
│     └── handle all input errors gracefully (empty, ctrl+c, etc.)
│
├── 3️⃣ Data: Model Format Mapping (≈ 20 lines)
│     └── dict with preferred structure format per model
│         e.g. {"claude": "xml", "gpt": "markdown", "qwen": "json"}
│
├── 4️⃣ Core: Prompt Analyzer (≈ 60 lines)
│     └── detect sections like:
│           - Task/Instruction
│           - Context
│           - Example
│           - Output requirements
│         parse heuristics using regex, keywords, sentence patterns
│
├── 5️⃣ Formatter Engine (≈ 70 lines)
│     └── takes structured dict and exports to chosen format:
│           - JSON: json.dumps()
│           - XML: xml.etree.ElementTree
│           - YAML: if available
│           - Markdown: templated headers
│
├── 6️⃣ Suggestion Engine (≈ 20 lines)
│     └── choose best format based on model name or user preference
│
├── 7️⃣ CLI Handler (≈ 60 lines)
│     └── parse CLI args or interactive loop:
│           "Enter your prompt:"
│           "Target model [gpt/claude/qwen/deepseek/etc]:"
│           -> show cleaned + formatted result
│           -> ask if they want to save output
│
├── 8️⃣ Error Handling + Recovery (≈ 20 lines)
│     └── wraps all major steps in try/except
│         -> fallback outputs + helpful error messages
│
└── 9️⃣ Main Runner (≈ 10 lines)
