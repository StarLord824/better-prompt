#!/usr/bin/env python3
"""
better_prompt_cli.py - AI Prompt Refinement Tool
Single-file CLI for refining prompts across multiple AI providers.
Install: pip install rich inquirer pyyaml
"""

import json
import re
import sys
from typing import Dict, Tuple, Optional, Callable
from xml.etree import ElementTree as ET

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.table import Table
    from rich import box
    import inquirer
except ImportError:
    print("Error: Install required packages: pip install rich inquirer pyyaml")
    sys.exit(1)

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

console = Console()

# ============================================================================
# MODEL-FORMAT MATRIX
# ============================================================================

MODEL_MATRIX = {
    "OpenAI": {
        "GPT-4o": "json", "GPT-4 Turbo": "json",
        "GPT-3.5 Turbo": "yaml", "GPT-4-mini": "json"
    },
    "Anthropic": {
        "Claude 3.5 Sonnet": "xml", "Claude 3.5 Haiku": "xml",
        "Claude 3 Opus": "yaml", "Claude Instant": "xml"
    },
    "Google": {
        "Gemini 1.5 Pro": "yaml", "Gemini 1.5 Flash": "json",
        "Gemini 2.0 Experimental": "json"
    },
    "DeepSeek": {
        "DeepSeek Chat": "yaml", "DeepSeek Coder": "json",
        "DeepSeek R1": "yaml"
    },
    "Alibaba": {
        "Qwen 2.5": "json", "Qwen Max": "yaml", "Qwen Plus": "xml"
    },
    "X": {
        "Grok 3": "yaml", "Grok 2": "json", "Grok Beta": "yaml"
    }
}

BANNER = """[bold cyan]
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ██████╗ ███████╗████████╗████████╗███████╗██████╗       ║
║   ██╔══██╗██╔════╝╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗      ║
║   ██████╔╝█████╗     ██║      ██║   █████╗  ██████╔╝      ║
║   ██╔══██╗██╔══╝     ██║      ██║   ██╔══╝  ██╔══██╗      ║
║   ██████╔╝███████╗   ██║      ██║   ███████╗██║  ██║      ║
║   ╚═════╝ ╚══════╝   ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝      ║
║                                                           ║
║      AI Prompt Refinement & Optimizer Tool v1.0           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
# BANNER = """[bold cyan]
# ╔═══════════════════════════════════════════════╗
# ║         BETTER-PROMPT v2.0                      ║
# ║    AI Prompt Refinement & Optimizer           ║
# ╚═══════════════════════════════════════════════╝[/]"""

# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def analyze_prompt(text: str) -> Dict[str, str]:
    """Parse prompt into semantic sections."""
    sections = {"context": "", "instruction": "", "examples": "", "constraints": ""}
    text = text.strip()
    if not text:
        return sections
    
    # Extract context
    ctx = re.search(r'(?:context|background|given)[:\s]+(.+?)(?=\n\n|\Z)', text, re.I | re.S)
    if ctx:
        sections["context"] = ctx.group(1).strip()
        text = text.replace(ctx.group(0), "")
    
    # Extract examples
    ex = re.search(r'(?:example|for instance)[:\s]+(.+?)(?=\n\n|\Z)', text, re.I | re.S)
    if ex:
        sections["examples"] = ex.group(1).strip()
        text = text.replace(ex.group(0), "")
    
    # Extract constraints
    con = re.search(r'(?:format|output|must be|should be)[:\s]+(.+?)(?=\n\n|\Z)', text, re.I | re.S)
    if con:
        sections["constraints"] = con.group(1).strip()
        text = text.replace(con.group(0), "")
    
    sections["instruction"] = text.strip()
    return sections

def to_json(data: Dict) -> str:
    """Format as JSON."""
    return json.dumps({k: v for k, v in data.items() if v}, indent=2, ensure_ascii=False)

def to_xml(data: Dict) -> str:
    """Format as XML."""
    root = ET.Element("prompt")
    for k, v in data.items():
        if v:
            child = ET.SubElement(root, k)
            child.text = v
    return ET.tostring(root, encoding='unicode', method='xml')

def to_yaml(data: Dict) -> str:
    """Format as YAML."""
    if not HAS_YAML:
        return "# YAML unavailable\n" + to_json(data)
    return yaml.dump({k: v for k, v in data.items() if v}, allow_unicode=True, sort_keys=False)

def to_markdown(data: Dict) -> str:
    """Format as Markdown."""
    lines = ["# Refined Prompt\n"]
    mapping = {"instruction": "Task", "context": "Context", "examples": "Examples", "constraints": "Requirements"}
    for k, title in mapping.items():
        if data.get(k):
            lines.append(f"## {title}\n{data[k]}\n")
    return "\n".join(lines)

FORMATTERS = {"json": to_json, "xml": to_xml, "yaml": to_yaml, "markdown": to_markdown}

# ============================================================================
# PLUGIN SYSTEM
# ============================================================================

class PluginManager:
    """Manages external plugin loading with error handling."""
    
    def __init__(self):
        self.plugins: Dict[str, Callable] = {}
        self._discover_plugins()
    
    def _discover_plugins(self):
        """Safely discover and load plugins from external modules."""
        plugin_names = ["PromptRefiner", "LLMDirect", "PromptLinter"]
        
        for name in plugin_names:
            try:
                # Attempt dynamic import (safe - doesn't crash if plugin missing)
                module = __import__(f"plugins.{name.lower()}", fromlist=[name])
                if hasattr(module, 'process_prompt'):
                    self.plugins[name] = module.process_prompt
                    console.print(f"[dim green]✓ Loaded plugin: {name}[/]")
            except (ImportError, AttributeError, Exception) as e:
                # Plugin doesn't exist or has errors - gracefully skip
                console.print(f"[dim yellow]⚠ Plugin {name} unavailable: {type(e).__name__}[/]")
                continue
    
    def apply_plugin(self, plugin_name: str, prompt: str, metadata: Dict) -> Optional[Dict]:
        """Apply plugin safely with error handling."""
        if plugin_name not in self.plugins:
            return None
        
        try:
            result = self.plugins[plugin_name](prompt, metadata)
            if isinstance(result, dict):
                return result
        except Exception as e:
            console.print(f"[red]✗ Plugin {plugin_name} error: {e}[/]")
        return None
    
    def list_available(self) -> list:
        """Return list of loaded plugins."""
        return list(self.plugins.keys())

# ============================================================================
# USER INTERFACE
# ============================================================================

def get_prompt_input() -> str:
    """Get multi-line prompt from user."""
    console.print("[bold yellow]Enter your prompt[/] [dim](Ctrl+D or empty line twice to finish)[/]")
    lines, empty = [], 0
    while True:
        try:
            line = input()
            if not line:
                empty += 1
                if empty >= 2:
                    break
            else:
                empty = 0
                lines.append(line)
        except (EOFError, KeyboardInterrupt):
            break
    return '\n'.join(lines).strip()

def select_provider_and_model() -> Tuple[str, str, str]:
    """Interactive provider and model selection."""
    try:
        providers = list(MODEL_MATRIX.keys())
        q1 = [inquirer.List('provider', message="Select AI Provider", choices=providers)]
        provider = inquirer.prompt(q1)['provider']
        
        models = list(MODEL_MATRIX[provider].keys())
        q2 = [inquirer.List('model', message=f"Select {provider} Model", choices=models)]
        model = inquirer.prompt(q2)['model']
        
        format_type = MODEL_MATRIX[provider][model]
        return provider, model, format_type
    except (KeyError, TypeError, Exception) as e:
        console.print(f"[red]Selection error: {e}. Using defaults.[/]")
        return "OpenAI", "GPT-4o", "json"

def display_result(prompt: str, sections: Dict, format_type: str, provider: str, model: str):
    """Display refined prompt with syntax highlighting."""
    formatter = FORMATTERS.get(format_type, to_markdown)
    output = formatter(sections)
    
    # Syntax mapping
    syntax_lang = {"json": "json", "xml": "xml", "yaml": "yaml", "markdown": "markdown"}
    
    console.print(Panel(
        f"[bold green]Provider:[/] {provider}\n"
        f"[bold green]Model:[/] {model}\n"
        f"[bold green]Format:[/] {format_type.upper()}",
        title="[bold cyan]Refinement Complete[/]",
        box=box.DOUBLE
    ))
    
    console.print("\n[bold yellow]Original Prompt:[/]")
    console.print(Panel(prompt[:200] + "..." if len(prompt) > 200 else prompt, box=box.ROUNDED))
    
    console.print("\n[bold yellow]Refined Output:[/]")
    syntax = Syntax(output, syntax_lang.get(format_type, "text"), theme="monokai", line_numbers=True)
    console.print(Panel(syntax, box=box.ROUNDED, border_style="cyan"))
    
    # Save option
    try:
        save = inquirer.confirm("Save to file?", default=False)
        if save:
            filename = inquirer.text("Filename", default=f"prompt.{format_type}")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(output)
            console.print(f"[green]✓ Saved to {filename}[/]")
    except Exception as e:
        console.print(f"[red]Save error: {e}[/]")

def show_plugin_options(manager: PluginManager, prompt: str, metadata: Dict) -> Dict:
    """Allow user to select and apply plugins."""
    available = manager.list_available()
    if not available:
        return analyze_prompt(prompt)
    
    try:
        choices = ["None (skip plugins)"] + available
        q = [inquirer.List('plugin', message="Apply plugin enhancement?", choices=choices)]
        selection = inquirer.prompt(q)['plugin']
        
        if selection != "None (skip plugins)":
            console.print(f"[cyan]Applying {selection}...[/]")
            result = manager.apply_plugin(selection, prompt, metadata)
            if result:
                return result
    except Exception as e:
        console.print(f"[yellow]Plugin selection error: {e}[/]")
    
    return analyze_prompt(prompt)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry."""
    try:
        console.print(BANNER)
        console.print(Panel("[dim]Refine prompts for any AI model with perfect formatting[/]", box=box.ROUNDED))
        
        # Initialize plugin system
        plugin_manager = PluginManager()
        
        # Step 1: Get prompt
        prompt = get_prompt_input()
        if not prompt:
            console.print("[red]No prompt entered. Exiting.[/]")
            return
        
        # Step 2: Select provider and model
        provider, model, format_type = select_provider_and_model()
        
        # Step 3: Apply plugins or analyze
        metadata = {"provider": provider, "model": model, "format": format_type}
        sections = show_plugin_options(plugin_manager, prompt, metadata)
        
        # Step 4: Display results
        with console.status("[bold cyan]Processing...", spinner="dots"):
            import time
            time.sleep(1)  # Simulate processing
        
        display_result(prompt, sections, format_type, provider, model)
        
        # Loop option
        if inquirer.confirm("Refine another prompt?", default=False):
            console.clear()
            main()
        else:
            console.print("\n[bold green]Thank you for using Better-Prompt! 🚀[/]")
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user.[/]")
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/]")
        console.print("[dim]Please report this issue.[/]")

if __name__ == "__main__":
    main()