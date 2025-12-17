"""
Better Prompt CLI - Main Application

A beautiful command-line interface for prompt optimization.
"""

import typer
from typing import Optional, List
from pathlib import Path
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich import print as rprint

from ..core.pipeline import PipelineOrchestrator
from ..core.classifier import TaskClassifier
from ..core.format_selector import FormatSelector, OutputFormat
from ..core.refiner import ToneType
from ..core.plugins import PluginRegistry

app = typer.Typer(
    name="better-prompt",
    help="🚀 Better Prompt - Transform your prompts, elevate your results",
    add_completion=False,
)

console = Console()


# ============================================================================
# MAIN COMMAND: Process a prompt
# ============================================================================

@app.command("process")
def process_prompt(
    prompt: Optional[str] = typer.Argument(
        None,
        help="The prompt to process. If not provided, will prompt interactively."
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model", "-m",
        help="Target model (e.g., gpt-4, claude-3-opus)"
    ),
    provider: Optional[str] = typer.Option(
        None,
        "--provider", "-p",
        help="Model provider (e.g., OpenAI, Anthropic, Google)"
    ),
    tone: Optional[str] = typer.Option(
        "professional",
        "--tone", "-t",
        help="Tone: professional, casual, technical, creative, formal, friendly, neutral"
    ),
    output_format: Optional[str] = typer.Option(
        None,
        "--format", "-f",
        help="Output format: json, xml, yaml, markdown, text"
    ),
    no_template: bool = typer.Option(
        False,
        "--no-template",
        help="Don't apply format template"
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Save refined prompt to file"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Show detailed information"
    ),
):
    """
    Process and optimize a prompt for a specific model.
    
    Examples:
    
        better-prompt process "Write a Python function"
        
        better-prompt process "Create an image" -m gpt-4 -p OpenAI
        
        better-prompt process -t casual -f json
    """
    console.print("\n[bold cyan]🚀 Better Prompt - Prompt Optimizer[/bold cyan]\n")
    
    # Interactive mode if prompt not provided
    if not prompt:
        prompt = Prompt.ask("[bold yellow]Enter your prompt[/bold yellow]")
    
    # Interactive model selection if not provided
    if not model or not provider:
        if Confirm.ask("Would you like to specify a target model?", default=True):
            provider = _select_provider()
            model = _select_model(provider)
    
    # Convert tone string to ToneType
    try:
        tone_type = ToneType(tone.lower())
    except ValueError:
        console.print(f"[red]Invalid tone: {tone}. Using 'professional'[/red]")
        tone_type = ToneType.PROFESSIONAL
    
    # Process the prompt
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Processing prompt...", total=None)
        
        orchestrator = PipelineOrchestrator()
        result = orchestrator.process(
            prompt=prompt,
            model_name=model,
            provider=provider,
            tone=tone_type,
            apply_template=not no_template
        )
        
        progress.update(task, completed=True)
    
    # Display results
    _display_results(result, verbose)
    
    # Save to file if requested
    if output_file:
        _save_to_file(result, output_file)
        console.print(f"\n[green]✓ Saved to {output_file}[/green]")
    
    console.print()


# ============================================================================
# BATCH COMMAND: Process multiple prompts
# ============================================================================

@app.command("batch")
def batch_process(
    input_file: Path = typer.Argument(
        ...,
        help="JSON file containing prompts to process",
        exists=True
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model", "-m",
        help="Target model for all prompts"
    ),
    provider: Optional[str] = typer.Option(
        None,
        "--provider", "-p",
        help="Model provider for all prompts"
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Save results to JSON file"
    ),
):
    """
    Process multiple prompts from a JSON file.
    
    Input file format:
    {
        "prompts": [
            "Prompt 1",
            "Prompt 2",
            "Prompt 3"
        ]
    }
    
    Example:
        better-prompt batch prompts.json -m gpt-4 -p OpenAI -o results.json
    """
    console.print("\n[bold cyan]📦 Better Prompt - Batch Processing[/bold cyan]\n")
    
    # Load prompts
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            prompts = data.get("prompts", [])
    except Exception as e:
        console.print(f"[red]Error loading file: {e}[/red]")
        raise typer.Exit(1)
    
    if not prompts:
        console.print("[red]No prompts found in file[/red]")
        raise typer.Exit(1)
    
    console.print(f"[cyan]Found {len(prompts)} prompts to process[/cyan]\n")
    
    # Process prompts
    orchestrator = PipelineOrchestrator()
    
    with Progress(console=console) as progress:
        task = progress.add_task("[cyan]Processing prompts...", total=len(prompts))
        
        results = orchestrator.process_batch(
            prompts=prompts,
            model_name=model,
            provider=provider
        )
        
        progress.update(task, advance=len(prompts))
    
    # Display statistics
    stats = orchestrator.get_statistics(results)
    _display_batch_stats(stats)
    
    # Save results if requested
    if output_file:
        output_data = {
            "statistics": stats,
            "results": [
                {
                    "original": r.original_prompt,
                    "refined": r.refined_prompt,
                    "task_type": r.task_classification.task_type.value,
                    "confidence": r.task_classification.confidence,
                    "format": r.format_recommendation.recommended_format.value,
                }
                for r in results
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2)
        
        console.print(f"\n[green]✓ Results saved to {output_file}[/green]")
    
    console.print()


# ============================================================================
# CLASSIFY COMMAND: Just classify the task type
# ============================================================================

@app.command("classify")
def classify_prompt(
    prompt: str = typer.Argument(..., help="The prompt to classify"),
):
    """
    Classify a prompt to identify its task type.
    
    Example:
        better-prompt classify "Write a Python function"
    """
    console.print("\n[bold cyan]🔍 Better Prompt - Task Classifier[/bold cyan]\n")
    
    classifier = TaskClassifier()
    result = classifier.classify(prompt)
    
    # Display results
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Task Type", result.task_type.value)
    table.add_row("Confidence", f"{result.confidence:.0%}")
    table.add_row("Reasoning", result.reasoning)
    
    console.print(table)
    console.print()


# ============================================================================
# MODELS COMMAND: List supported models
# ============================================================================

@app.command("models")
def list_models(
    provider: Optional[str] = typer.Option(
        None,
        "--provider", "-p",
        help="Filter by provider"
    ),
    format_type: Optional[str] = typer.Option(
        None,
        "--format", "-f",
        help="Filter by preferred format"
    ),
):
    """
    List all supported models and their preferred formats.
    
    Examples:
        better-prompt models
        
        better-prompt models --provider OpenAI
        
        better-prompt models --format json
    """
    console.print("\n[bold cyan]📋 Better Prompt - Supported Models[/bold cyan]\n")
    
    selector = FormatSelector()
    models = selector.list_supported_models()
    
    # Filter by provider if specified
    if provider:
        models = [m for m in models if m.lower().startswith(provider.lower())]
    
    # Filter by format if specified
    if format_type:
        try:
            fmt = OutputFormat(format_type.lower())
            models = selector.get_models_by_format(fmt)
        except ValueError:
            console.print(f"[red]Invalid format: {format_type}[/red]")
            raise typer.Exit(1)
    
    # Display in table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Provider", style="cyan")
    table.add_column("Model", style="green")
    table.add_column("Preferred Format", style="yellow")
    
    for model_path in models:
        provider_name, model_name = model_path.split("/")
        result = selector.recommend_format(model_name=model_name, provider=provider_name)
        table.add_row(provider_name, model_name, result.recommended_format.value)
    
    console.print(table)
    console.print(f"\n[cyan]Total: {len(models)} models[/cyan]\n")


# ============================================================================
# INFO COMMAND: Show system information
# ============================================================================

@app.command("info")
def show_info():
    """
    Show Better Prompt system information.
    """
    from .. import __version__
    
    console.print("\n[bold cyan]ℹ️  Better Prompt - System Information[/bold cyan]\n")
    
    info_table = Table(show_header=False, box=None)
    info_table.add_column("Property", style="cyan")
    info_table.add_column("Value", style="green")
    
    info_table.add_row("Version", __version__)
    info_table.add_row("Task Types", "15+")
    info_table.add_row("Supported Models", "37+")
    info_table.add_row("Output Formats", "5")
    info_table.add_row("Tone Options", "7")
    
    console.print(info_table)
    
    # Show available components
    console.print("\n[bold]Available Components:[/bold]")
    components = [
        "✓ Task Classifier",
        "✓ Format Selector",
        "✓ Refinement Pipeline",
        "✓ Pipeline Orchestrator",
        "✓ Plugin System",
        "✓ LLM Gateway"
    ]
    for comp in components:
        console.print(f"  [green]{comp}[/green]")
    
    console.print()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _select_provider() -> str:
    """Interactive provider selection."""
    providers = ["OpenAI", "Anthropic", "Google", "Alibaba", "DeepSeek", "xAI"]
    
    console.print("\n[bold]Select Provider:[/bold]")
    for i, p in enumerate(providers, 1):
        console.print(f"  {i}. {p}")
    
    choice = Prompt.ask(
        "Enter number",
        choices=[str(i) for i in range(1, len(providers) + 1)],
        default="1"
    )
    
    return providers[int(choice) - 1]


def _select_model(provider: str) -> str:
    """Interactive model selection based on provider."""
    models_by_provider = {
        "OpenAI": ["gpt-4", "gpt-4o", "gpt-4o-mini", "o1-research"],
        "Anthropic": ["claude-3-opus", "claude-3-sonnet", "claude-4-opus", "claude-4-haiku"],
        "Google": ["gemini-pro", "gemini-ultra", "gemini-1.5-viz", "palm-2-enterprise"],
        "Alibaba": ["qwen3-max", "qwen2.5-coder-32B", "qwen3-omni", "qwen2.5-vl"],
        "DeepSeek": ["deepseek-v3.1", "deepseek-r1-instruct", "deepseek-v2-lite", "deepseek-v3-coder"],
        "xAI": ["grok-4", "grok-code-fast", "grok-vision-2", "grok-agent-alpha"],
    }
    
    models = models_by_provider.get(provider, [])
    
    if not models:
        return Prompt.ask(f"Enter model name for {provider}")
    
    console.print(f"\n[bold]Select {provider} Model:[/bold]")
    for i, m in enumerate(models, 1):
        console.print(f"  {i}. {m}")
    
    choice = Prompt.ask(
        "Enter number",
        choices=[str(i) for i in range(1, len(models) + 1)],
        default="1"
    )
    
    return models[int(choice) - 1]


def _display_results(result, verbose: bool = False):
    """Display processing results."""
    # Task Classification
    console.print(Panel(
        f"[bold]Task Type:[/bold] {result.task_classification.task_type.value}\n"
        f"[bold]Confidence:[/bold] {result.task_classification.confidence:.0%}",
        title="[bold cyan]Classification[/bold cyan]",
        border_style="cyan"
    ))
    
    # Format Recommendation
    console.print(Panel(
        f"[bold]Format:[/bold] {result.format_recommendation.recommended_format.value}\n"
        f"[bold]Confidence:[/bold] {result.format_recommendation.confidence:.0%}",
        title="[bold green]Format[/bold green]",
        border_style="green"
    ))
    
    # Improvements
    if result.refinement_result.improvements:
        improvements_text = "\n".join(
            f"  • {imp}" for imp in result.refinement_result.improvements
        )
        console.print(Panel(
            improvements_text,
            title="[bold yellow]Improvements[/bold yellow]",
            border_style="yellow"
        ))
    
    # Refined Prompt
    console.print(Panel(
        result.refined_prompt,
        title="[bold magenta]Refined Prompt[/bold magenta]",
        border_style="magenta"
    ))
    
    # Verbose information
    if verbose:
        console.print("\n[bold]Detailed Information:[/bold]")
        console.print(f"  Stages Applied: {', '.join(result.refinement_result.stages_applied)}")
        console.print(f"  Timestamp: {result.timestamp}")


def _display_batch_stats(stats: dict):
    """Display batch processing statistics."""
    console.print("\n[bold cyan]📊 Processing Statistics[/bold cyan]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Prompts", str(stats["total_prompts"]))
    table.add_row("Avg Task Confidence", f"{stats['average_task_confidence']:.0%}")
    table.add_row("Avg Format Confidence", f"{stats['average_format_confidence']:.0%}")
    table.add_row("Total Improvements", str(stats["total_improvements"]))
    
    console.print(table)
    
    # Task distribution
    console.print("\n[bold]Task Type Distribution:[/bold]")
    for task, count in stats["task_type_distribution"].items():
        console.print(f"  {task}: {count}")
    
    # Format distribution
    console.print("\n[bold]Format Distribution:[/bold]")
    for fmt, count in stats["format_distribution"].items():
        console.print(f"  {fmt}: {count}")


def _save_to_file(result, output_file: Path):
    """Save result to file."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result.refined_prompt)


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
