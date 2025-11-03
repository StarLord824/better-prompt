#!/usr/bin/env python3
"""
better_auth.py - AI Prompt Optimizer CLI Tool

A single-file CLI tool that analyzes natural language prompts and reformats them
into structured formats optimized for different AI models (Claude, GPT-4, Gemini, etc.).

Usage:
    python better_auth.py "Your prompt here" --model claude-4-opus
    python better_auth.py --demo
    echo "Summarize this text" | python better_auth.py -m gpt-4
    python better_auth.py -m qwen3-max -f json -o output.json

Supports: JSON, XML, YAML (if PyYAML installed), and Markdown formats.
"""

import sys
import json
import argparse
import re
from typing import Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET
from io import StringIO

# Optional dependency detection
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Model to format mappings
MODEL_FORMATS = {
    "gpt-4": "markdown", "gpt-4o": "markdown", "gpt-4o-mini": "markdown", "o1-research": "json",
    "claude-3-opus": "xml", "claude-3-sonnet": "xml", "claude-4-opus": "xml", "claude-4-haiku": "xml",
    "gemini-ultra": "yaml", "gemini-pro": "json", "palm-2-enterprise": "json", "gemini-1.5-viz": "markdown",
    "qwen3-max": "json", "qwen2.5-coder-32B": "json", "qwen3-omni": "json", "qwen2.5-vl": "yaml",
    "deepseek-v3.1": "json", "deepseek-r1-instruct": "json", "deepseek-v2-lite": "yaml", "deepseek-v3-coder": "json",
    "grok-4": "markdown", "grok-code-fast": "markdown", "grok-vision-2": "markdown", "grok-agent-alpha": "xml"
}


def sanitize_input(text: str) -> str:
    """Clean and normalize input text."""
    return text.strip() if text else ""


def analyze_prompt(prompt: str) -> Dict[str, str]:
    """
    Parse prompt into semantic sections using keyword heuristics and patterns.
    Returns dict with: task, context, examples, output_requirements.
    """
    prompt = sanitize_input(prompt)
    if not prompt:
        return {"task": "", "context": "", "examples": "", "output_requirements": ""}
    
    sections = {"task": "", "context": "", "examples": "", "output_requirements": ""}
    
    # Extract examples section
    example_match = re.search(r'(?:examples?|for instance|such as)[:\s]+(.+?)(?=\n\n|\Z)', prompt, re.IGNORECASE | re.DOTALL)
    if example_match:
        sections["examples"] = example_match.group(1).strip()
        prompt = prompt.replace(example_match.group(0), "")
    
    # Extract output requirements
    output_patterns = [r'(?:format|output|result|response)[:\s]+(.+?)(?=\n\n|\Z)', 
                      r'(?:should be|must be|needs to be)[:\s]+(.+?)(?=\n\n|\Z)']
    for pattern in output_patterns:
        match = re.search(pattern, prompt, re.IGNORECASE | re.DOTALL)
        if match:
            sections["output_requirements"] = match.group(1).strip()
            prompt = prompt.replace(match.group(0), "")
            break
    
    # Extract context (paragraphs with keywords)
    context_match = re.search(r'(?:context|background|given|about)[:\s]+(.+?)(?=\n\n|\Z)', prompt, re.IGNORECASE | re.DOTALL)
    if context_match:
        sections["context"] = context_match.group(1).strip()
        prompt = prompt.replace(context_match.group(0), "")
    
    # Remaining is the task
    sections["task"] = sanitize_input(prompt)
    
    return sections


def to_json(sections: Dict[str, str]) -> str:
    """Convert sections to JSON format."""
    return json.dumps(sections, indent=2, ensure_ascii=False)


def to_yaml(sections: Dict[str, str]) -> str:
    """Convert sections to YAML format (requires PyYAML)."""
    if not HAS_YAML:
        return "# YAML output requires PyYAML. Install: pip install pyyaml\n" + to_json(sections)
    return yaml.dump(sections, allow_unicode=True, default_flow_style=False, sort_keys=False)


def to_xml(sections: Dict[str, str]) -> str:
    """Convert sections to XML format."""
    root = ET.Element("prompt")
    for key, value in sections.items():
        child = ET.SubElement(root, key)
        child.text = value
    
    # Pretty print
    rough_string = ET.tostring(root, encoding='unicode')
    return rough_string.replace('><', '>\n<')


def to_markdown(sections: Dict[str, str]) -> str:
    """Convert sections to Markdown format."""
    lines = ["# Structured Prompt\n"]
    
    if sections.get("task"):
        lines.append("## Task")
        lines.append(sections["task"] + "\n")
    
    if sections.get("context"):
        lines.append("## Context")
        lines.append(sections["context"] + "\n")
    
    if sections.get("examples"):
        lines.append("## Examples")
        lines.append(sections["examples"] + "\n")
    
    if sections.get("output_requirements"):
        lines.append("## Output Requirements")
        lines.append(sections["output_requirements"] + "\n")
    
    return "\n".join(lines)


def validate_json(text: str) -> bool:
    """Check if text is valid JSON."""
    try:
        json.loads(text)
        return True
    except (json.JSONDecodeError, ValueError):
        return False


def validate_xml(text: str) -> bool:
    """Check if text is valid XML."""
    try:
        ET.fromstring(text)
        return True
    except ET.ParseError:
        return False


def format_prompt(sections: Dict[str, str], format_type: str) -> Tuple[str, bool]:
    """
    Format sections into specified format. Returns (formatted_text, is_valid).
    Falls back to markdown if validation fails.
    """
    formatters = {
        "json": to_json,
        "yaml": to_yaml,
        "xml": to_xml,
        "markdown": to_markdown
    }
    
    formatter = formatters.get(format_type.lower(), to_markdown)
    formatted = formatter(sections)
    
    # Validate if applicable
    is_valid = True
    if format_type.lower() == "json":
        is_valid = validate_json(formatted)
    elif format_type.lower() == "xml":
        is_valid = validate_xml(formatted)
    
    if not is_valid:
        print(f"Warning: {format_type.upper()} validation failed. Falling back to Markdown.", file=sys.stderr)
        formatted = to_markdown(sections)
    
    return formatted, is_valid


def get_default_format(model: str) -> str:
    """Get default format for a model."""
    return MODEL_FORMATS.get(model.lower(), "markdown")


def save_to_file(content: str, filename: str) -> bool:
    """Save content to file with overwrite protection."""
    import os
    
    if os.path.exists(filename):
        try:
            response = input(f"File '{filename}' exists. Overwrite? (y/n): ")
            if response.lower() != 'y':
                print("Save cancelled.")
                return False
        except (EOFError, KeyboardInterrupt):
            print("\nSave cancelled.")
            return False
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved to: {filename}")
        return True
    except IOError as e:
        print(f"Error saving file: {e}", file=sys.stderr)
        return False


def run_demo():
    """Run demonstration with example prompts."""
    examples = [
        {
            "prompt": "Summarize the following article in 5 bullet points. Article: Climate change affects global ecosystems. Context: This is for a high school presentation. Format: formal tone.",
            "model": "claude-4-opus",
            "format": "xml"
        },
        {
            "prompt": "Write a Python function that calculates Fibonacci numbers. Examples: fib(5) = 5, fib(10) = 55. Output: Include docstring and type hints.",
            "model": "qwen3-max",
            "format": "json"
        }
    ]
    
    print("=== DEMO MODE ===\n")
    for i, ex in enumerate(examples, 1):
        print(f"Example {i}: Model={ex['model']}, Format={ex['format']}")
        print(f"Input: {ex['prompt'][:80]}...\n")
        
        sections = analyze_prompt(ex['prompt'])
        formatted, _ = format_prompt(sections, ex['format'])
        print(formatted)
        print("\n" + "="*60 + "\n")


def read_multiline_input() -> str:
    """Read multiline input from stdin until EOF."""
    print("Enter your prompt (press Ctrl+D on Unix or Ctrl+Z on Windows when done):")
    try:
        lines = []
        while True:
            try:
                line = input()
                lines.append(line)
            except EOFError:
                break
        return "\n".join(lines)
    except KeyboardInterrupt:
        print("\nInput cancelled.")
        return ""


def self_test():
    """Run minimal self-tests on core functions."""
    test_prompt = "Summarize this text. Context: Testing. Output: JSON format."
    sections = analyze_prompt(test_prompt)
    
    # Test JSON
    json_out = to_json(sections)
    assert validate_json(json_out), "JSON validation failed"
    
    # Test XML
    xml_out = to_xml(sections)
    assert validate_xml(xml_out), "XML validation failed"
    
    # Test Markdown (always works)
    md_out = to_markdown(sections)
    assert len(md_out) > 0, "Markdown generation failed"
    
    print("Self-tests passed.")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Prompt Optimizer - Structure prompts for different AI models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  %(prog)s 'Summarize this article' -m claude-4-opus\n"
               "  %(prog)s --demo\n"
               "  echo 'Write a poem' | %(prog)s -m gpt-4"
    )
    
    parser.add_argument('prompt', nargs='?', help='Prompt text (or read from stdin)')
    parser.add_argument('-m', '--model', help='Target AI model')
    parser.add_argument('-f', '--format', choices=['json', 'yaml', 'xml', 'markdown'], 
                       help='Output format (overrides model default)')
    parser.add_argument('-o', '--out', help='Save output to file')
    parser.add_argument('--demo', action='store_true', help='Run demo examples')
    parser.add_argument('--test', action='store_true', help='Run self-tests')
    
    args = parser.parse_args()
    
    try:
        # Handle special modes
        if args.demo:
            run_demo()
            return 0
        
        if args.test:
            self_test()
            return 0
        
        # Get prompt text
        prompt_text = ""
        if args.prompt:
            prompt_text = args.prompt
        elif not sys.stdin.isatty():
            prompt_text = sys.stdin.read()
        else:
            prompt_text = read_multiline_input()
        
        if not prompt_text.strip():
            print("Error: No prompt provided.", file=sys.stderr)
            parser.print_help()
            return 1
        
        # Determine format
        if args.format:
            output_format = args.format
        elif args.model:
            output_format = get_default_format(args.model)
        else:
            output_format = "markdown"
        
        # Process prompt
        sections = analyze_prompt(prompt_text)
        formatted, is_valid = format_prompt(sections, output_format)
        
        # Output or save
        if args.out:
            save_to_file(formatted, args.out)
        else:
            print(formatted)
        
        return 0
        
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())