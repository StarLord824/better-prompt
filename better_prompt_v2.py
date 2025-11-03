import asyncio
import json
import re
import sys
from typing import Dict, List, Callable, Optional, Tuple
from enum import Enum

try:
    import click
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.panel import Panel
    from rich.table import Table
    from rich.spinner import Spinner
    from rich.syntax import Syntax
    from rich import box
    from rich.markdown import Markdown
except ImportError:
    print("Error: Required packages not found.")
    print("Install with: pip install rich click aiohttp")
    sys.exit(1)

# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

ASCII_LOGO = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ██████╗ ███████╗████████╗████████╗███████╗██████╗       ║
║   ██╔══██╗██╔════╝╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗      ║
║   ██████╔╝█████╗     ██║      ██║   █████╗  ██████╔╝      ║
║   ██╔══██╗██╔══╝     ██║      ██║   ██╔══╝  ██╔══██╗      ║
║   ██████╔╝███████╗   ██║      ██║   ███████╗██║  ██║      ║
║   ╚═════╝ ╚══════╝   ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝      ║
║                                                           ║
║            AI Prompt Refinement Tool v2.0                 ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""

# Model Provider Mappings
MODEL_PROVIDERS = {
    "OpenAI": {
        "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo", "o1-preview"],
        "format_type": "markdown",
        "api_format": '{"role": "user", "content": "{prompt}"}'
    },
    "Anthropic": {
        "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku", "claude-4-opus"],
        "format_type": "xml",
        "api_format": '{"role": "user", "content": "{prompt}"}'
    },
    "Google": {
        "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-ultra"],
        "format_type": "json",
        "api_format": '{"role": "user", "parts": [{"text": "{prompt}"}]}'
    },
    "Alibaba": {
        "models": ["qwen2.5", "qwen1.5-72b", "qwen-max", "qwen3-omni"],
        "format_type": "json",
        "api_format": '{"messages": [{"role": "user", "content": "{prompt}"}]}'
    },
    "DeepSeek": {
        "models": ["deepseek-coder", "deepseek-chat", "deepseek-v3"],
        "format_type": "json",
        "api_format": '{"messages": [{"role": "user", "content": "{prompt}"}]}'
    },
    "xAI": {
        "models": ["grok-2", "grok-vision", "grok-beta"],
        "format_type": "markdown",
        "api_format": '{"prompt": "{prompt}"}'
    }
}

console = Console()

# ============================================================================
# PROMPT ANALYSIS ENGINE
# ============================================================================

def analyze_prompt(prompt: str) -> Dict[str, str]:
    """Parse prompt into semantic sections."""
    prompt = prompt.strip()
    if not prompt:
        return {"task": "", "context": "", "examples": "", "output_requirements": ""}
    
    sections = {"task": "", "context": "", "examples": "", "output_requirements": ""}
    
    # Extract examples
    example_match = re.search(
        r'(?:examples?|for instance|such as)[:\s]+(.+?)(?=\n\n|\Z)',
        prompt, re.IGNORECASE | re.DOTALL
    )
    if example_match:
        sections["examples"] = example_match.group(1).strip()
        prompt = prompt.replace(example_match.group(0), "")
    
    # Extract output requirements
    output_patterns = [
        r'(?:format|output|result|response)[:\s]+(.+?)(?=\n\n|\Z)',
        r'(?:should be|must be|needs to be)[:\s]+(.+?)(?=\n\n|\Z)'
    ]
    for pattern in output_patterns:
        match = re.search(pattern, prompt, re.IGNORECASE | re.DOTALL)
        if match:
            sections["output_requirements"] = match.group(1).strip()
            prompt = prompt.replace(match.group(0), "")
            break
    
    # Extract context
    context_match = re.search(
        r'(?:context|background|given|about)[:\s]+(.+?)(?=\n\n|\Z)',
        prompt, re.IGNORECASE | re.DOTALL
    )
    if context_match:
        sections["context"] = context_match.group(1).strip()
        prompt = prompt.replace(context_match.group(0), "")
    
    sections["task"] = prompt.strip()
    return sections

# ============================================================================
# FORMATTERS
# ============================================================================

def format_as_json(sections: Dict[str, str]) -> str:
    """Format as JSON."""
    return json.dumps(sections, indent=2, ensure_ascii=False)

def format_as_xml(sections: Dict[str, str]) -> str:
    """Format as XML."""
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<prompt>']
    for key, value in sections.items():
        if value:
            lines.append(f'  <{key}>{value}</{key}>')
    lines.append('</prompt>')
    return '\n'.join(lines)

def format_as_markdown(sections: Dict[str, str]) -> str:
    """Format as Markdown."""
    lines = ["# Optimized Prompt\n"]
    
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

def format_as_yaml(sections: Dict[str, str]) -> str:
    """Format as YAML."""
    lines = ["---"]
    for key, value in sections.items():
        if value:
            lines.append(f"{key}: |")
            for line in value.split('\n'):
                lines.append(f"  {line}")
    return '\n'.join(lines)

# ============================================================================
# PLUGIN SYSTEM
# ============================================================================

class PluginRegistry:
    """Registry for prompt refinement plugins."""
    
    def __init__(self):
        self.plugins: Dict[str, Callable] = {}
        self._register_default_plugins()
    
    def _register_default_plugins(self):
        """Register built-in plugins."""
        self.plugins = {
            "DirectFormatter": self._direct_formatter,
            "LangChainRefiner": self._langchain_refiner,
            "OpenRouterAdapter": self._openrouter_adapter,
            "None": lambda p, f: (p, "text")
        }
    
    def _direct_formatter(self, prompt: str, format_type: str) -> Tuple[str, str]:
        """Format prompt directly based on model requirements."""
        sections = analyze_prompt(prompt)
        
        formatters = {
            "json": format_as_json,
            "xml": format_as_xml,
            "markdown": format_as_markdown,
            "yaml": format_as_yaml
        }
        
        formatter = formatters.get(format_type, format_as_markdown)
        return formatter(sections), format_type
    
    def _langchain_refiner(self, prompt: str, format_type: str) -> Tuple[str, str]:
        """Simulate LangChain-style refinement with enhanced structure."""
        sections = analyze_prompt(prompt)
        
        # Add LangChain-specific enhancements
        enhanced = {
            "instruction": sections["task"],
            "context": sections["context"] or "No additional context provided.",
            "examples": sections["examples"] or "No examples provided.",
            "constraints": sections["output_requirements"] or "Follow best practices.",
            "chain_of_thought": "Think step by step before responding."
        }
        
        return format_as_json(enhanced), "json"
    
    def _openrouter_adapter(self, prompt: str, format_type: str) -> Tuple[str, str]:
        """Adapt prompt for OpenRouter unified API."""
        sections = analyze_prompt(prompt)
        
        openrouter_format = {
            "messages": [
                {
                    "role": "system",
                    "content": f"Context: {sections.get('context', 'N/A')}"
                },
                {
                    "role": "user",
                    "content": sections["task"]
                }
            ],
            "examples": sections.get("examples", ""),
            "requirements": sections.get("output_requirements", "")
        }
        
        return format_as_json(openrouter_format), "json"
    
    def get_plugin_names(self) -> List[str]:
        """Get list of available plugin names."""
        return list(self.plugins.keys())
    
    def process_with_plugin(self, plugin_name: str, prompt: str, 
                          format_type: str) -> Tuple[str, str]:
        """Process prompt with selected plugin."""
        plugin = self.plugins.get(plugin_name, self.plugins["None"])
        return plugin(prompt, format_type)

# ============================================================================
# UI HELPERS
# ============================================================================

def display_welcome():
    """Display welcome screen."""
    console.print(ASCII_LOGO, style="bold cyan")
    console.print(
        Panel(
            "[bold yellow]Welcome to Better Prompt CLI![/]\n\n"
            "This tool helps you refine and optimize prompts for different AI models.\n"
            "Select your provider, model, and optional plugins for best results.",
            box=box.ROUNDED,
            border_style="cyan"
        )
    )
    console.print()

def get_user_prompt() -> str:
    """Get prompt input from user."""
    console.print("[bold green]Step 1:[/] Enter your prompt", style="bold")
    console.print("[dim]Tip: You can paste multi-line prompts. Press Enter twice to finish.[/]\n")
    
    lines = []
    empty_count = 0
    
    while True:
        try:
            line = input()
            if not line:
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
                lines.append(line)
        except EOFError:
            break
    
    return '\n'.join(lines).strip()

def select_provider() -> str:
    """Interactive provider selection."""
    console.print("\n[bold green]Step 2:[/] Select AI Provider", style="bold")
    
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("№", style="cyan", width=4)
    table.add_column("Provider", style="green")
    table.add_column("Models Available", style="yellow")
    
    providers = list(MODEL_PROVIDERS.keys())
    for i, provider in enumerate(providers, 1):
        model_count = len(MODEL_PROVIDERS[provider]["models"])
        table.add_row(str(i), provider, f"{model_count} models")
    
    console.print(table)
    
    choice = Prompt.ask(
        "\n[bold cyan]Choose provider[/]",
        choices=[str(i) for i in range(1, len(providers) + 1)],
        default="1"
    )
    
    return providers[int(choice) - 1]

def select_model(provider: str) -> str:
    """Interactive model selection."""
    console.print(f"\n[bold green]Step 3:[/] Select Model from {provider}", style="bold")
    
    models = MODEL_PROVIDERS[provider]["models"]
    
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("№", style="cyan", width=4)
    table.add_column("Model Name", style="green")
    
    for i, model in enumerate(models, 1):
        table.add_row(str(i), model)
    
    console.print(table)
    
    choice = Prompt.ask(
        "\n[bold cyan]Choose model[/]",
        choices=[str(i) for i in range(1, len(models) + 1)],
        default="1"
    )
    
    return models[int(choice) - 1]

def select_plugin(registry: PluginRegistry) -> str:
    """Interactive plugin selection."""
    console.print("\n[bold green]Step 4:[/] Select Plugin (Optional)", style="bold")
    
    plugins = registry.get_plugin_names()
    
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("№", style="cyan", width=4)
    table.add_column("Plugin Name", style="green")
    table.add_column("Description", style="yellow")
    
    descriptions = {
        "DirectFormatter": "Standard format optimization",
        "LangChainRefiner": "Enhanced with chain-of-thought",
        "OpenRouterAdapter": "OpenRouter API compatible",
        "None": "No plugin (raw prompt)"
    }
    
    for i, plugin in enumerate(plugins, 1):
        table.add_row(str(i), plugin, descriptions.get(plugin, "Custom plugin"))
    
    console.print(table)
    
    choice = Prompt.ask(
        "\n[bold cyan]Choose plugin[/]",
        choices=[str(i) for i in range(1, len(plugins) + 1)],
        default="1"
    )
    
    return plugins[int(choice) - 1]

async def simulate_processing():
    """Simulate processing with spinner."""
    with console.status("[bold cyan]Refining your prompt...", spinner="dots"):
        await asyncio.sleep(1.5)  # Simulate processing time

def display_result(refined_prompt: str, format_type: str, provider: str, model: str):
    """Display the refined prompt with beautiful formatting."""
    console.print("\n" + "="*70 + "\n")
    
    console.print(
        Panel(
            f"[bold green]✓ Prompt Optimized Successfully![/]\n\n"
            f"[cyan]Provider:[/] {provider}\n"
            f"[cyan]Model:[/] {model}\n"
            f"[cyan]Format:[/] {format_type.upper()}",
            box=box.DOUBLE,
            border_style="green"
        )
    )
    
    console.print("\n[bold yellow]Refined Prompt:[/]\n")
    
    # Syntax highlighting based on format
    syntax_map = {
        "json": "json",
        "xml": "xml",
        "markdown": "markdown",
        "yaml": "yaml",
        "text": "text"
    }
    
    syntax = Syntax(
        refined_prompt,
        syntax_map.get(format_type, "text"),
        theme="monokai",
        line_numbers=True,
        word_wrap=True
    )
    
    console.print(Panel(syntax, box=box.ROUNDED, border_style="blue"))
    
    # Ask to save
    if Confirm.ask("\n[bold cyan]Save to file?[/]", default=False):
        filename = Prompt.ask(
            "[bold cyan]Enter filename[/]",
            default=f"refined_prompt.{format_type}"
        )
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(refined_prompt)
            console.print(f"[green]✓ Saved to {filename}[/]")
        except Exception as e:
            console.print(f"[red]✗ Error saving file: {e}[/]")

# ============================================================================
# MAIN APPLICATION
# ============================================================================

async def main_async():
    """Main application logic."""
    try:
        # Welcome screen
        display_welcome()
        
        # Step 1: Get prompt
        user_prompt = get_user_prompt()
        if not user_prompt:
            console.print("[red]Error: No prompt provided. Exiting.[/]")
            return
        
        # Step 2: Select provider
        provider = select_provider()
        
        # Step 3: Select model
        model = select_model(provider)
        
        # Step 4: Select plugin
        registry = PluginRegistry()
        plugin = select_plugin(registry)
        
        # Get format type for provider
        format_type = MODEL_PROVIDERS[provider]["format_type"]
        
        # Step 5: Process prompt
        await simulate_processing()
        
        refined_prompt, actual_format = registry.process_with_plugin(
            plugin, user_prompt, format_type
        )
        
        # Step 6: Display results
        display_result(refined_prompt, actual_format, provider, model)
        
        # Ask to run again
        console.print()
        if Confirm.ask("[bold cyan]Refine another prompt?[/]", default=True):
            console.clear()
            await main_async()
        else:
            console.print("\n[bold green]Thank you for using Better Prompt CLI! 🚀[/]\n")
    
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Operation cancelled by user.[/]")
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/]")
        console.print("[yellow]Please report this issue.[/]")

@click.command()
def main():
    """Entry point for the CLI application."""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/]")

if __name__ == "__main__":
    main()