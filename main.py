import sys, json, re, textwrap
import xml.etree.ElementTree as ET
try: import yaml
except: yaml = None

MODEL_FORMATS = {
  "OpenAI": { "gpt-4": "markdown", "gpt-4o": "markdown", "gpt-4o-mini": "markdown", "o1-research": "json" },
  "Anthropic": { "claude-3-opus": "xml", "claude-3-sonnet": "xml", "claude-4-opus": "xml", "claude-4-haiku": "xml"},
  "Google": { "gemini-ultra": "yaml", "gemini-pro": "json", "palm-2-enterprise": "json", "gemini-1.5-viz": "markdown" },
  "Alibaba": { "qwen3-max": "json", "qwen2.5-coder-32B": "json", "qwen3-omni": "json", "qwen2.5-vl": "yaml" },
  "DeepSeek": { "deepseek-v3.1": "json", "deepseek-r1-instruct": "json", "deepseek-v2-lite": "yaml", "deepseek-v3-coder": "json" },
  "xAI": { "grok-4": "markdown", "grok-code-fast": "markdown", "grok-vision-2": "markdown", "grok-agent-alpha": "xml" }
}

def safe_input(prompt):
    try:
        val = input(prompt).strip()
        if not val: raise ValueError("Empty input")
        return val
    except (EOFError, KeyboardInterrupt):
        print("\nExiting gracefully."); sys.exit(0)
    except Exception as e:
        print(f"[Warning] {e}, try again.")
        return safe_input(prompt)

def analyze_prompt(text):
    text = textwrap.dedent(text)
    sections = {}
    if "example" in text.lower(): 
        parts = text.split("example",1)
        sections["task"] = parts[0]
        sections["example"] = parts[1]
    elif "context" in text.lower():
        parts = text.split("context",1)
        sections["context"] = parts[1]
        sections["task"] = parts[0]
    else:
        sections["task"] = text
    return sections

def best_format_for_model(model):
    model = model.lower()
    return MODEL_FORMATS.get(model, "markdown")

def main():
    print("🧠 Better-Auth — AI Prompt Optimizer")
    model = safe_input("Target Model (gpt/claude/gemini/...): ")
    fmt = best_format_for_model(model)
    text = safe_input("Enter your raw prompt:\n> ")
    analyzed = analyze_prompt(text)

    print(f"\nOptimizing for {model} in {fmt.upper()}...\n")
    try:
        if fmt=="json": out = to_json(analyzed)
        elif fmt=="xml": out = to_xml(analyzed)
        elif fmt=="yaml": out = to_yaml(analyzed)
        else: out = to_markdown(analyzed)
        print(out)
    except Exception as e:
        print(f"[Error] Formatting failed: {e}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
