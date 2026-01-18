"""CLI entry point using typer."""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.json import JSON
from rich.table import Table

from promptlang.core.cache.manager import CacheManager
from promptlang.core.ir.validator import IRValidator
from promptlang.core.optimizer.token_optimizer import TokenOptimizer
from promptlang.core.pipeline.orchestrator import PipelineOrchestrator

app = typer.Typer(name="promptlang", help="PromptLang Compiler Platform CLI")
console = Console()


@app.command()
def generate(
    input_text: str = typer.Argument(..., help="Human input text"),
    model: str = typer.Option("oss", "--model", "-m", help="Target model (claude/gpt/oss)"),
    budget: int = typer.Option(4000, "--budget", "-b", help="Token budget"),
    security: str = typer.Option("high", "--security", "-s", help="Security level (low/high)"),
    scaffold_mode: str = typer.Option("full", "--scaffold-mode", help="Scaffold mode (quick/full)"),
    intent: Optional[str] = typer.Option(None, "--intent", "-i", help="Explicit intent"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """Generate prompt and scaffold from human input."""
    console.print(f"[bold green]Generating scaffold for:[/bold green] {input_text[:50]}...")

    async def run():
        cache_manager = CacheManager()
        orchestrator = PipelineOrchestrator(cache_manager=cache_manager)

        try:
            result = await orchestrator.execute(
                input_text=input_text,
                intent=intent,
                target_model=model,
                token_budget=budget,
                scaffold_mode=scaffold_mode,
                security_level=security,
                validation_mode="strict",
            )

            # Display result
            if output_file:
                with open(output_file, "w") as f:
                    json.dump(result, f, indent=2)
                console.print(f"[green]Result saved to:[/green] {output_file}")
            else:
                console.print("\n[bold]Generated Output:[/bold]")
                console.print(result["output"])

                if result.get("warnings"):
                    console.print("\n[bold yellow]Warnings:[/bold yellow]")
                    for warning in result["warnings"]:
                        console.print(f"  - {warning}")

                # Show validation status
                validation = result.get("validation_report", {})
                status = validation.get("status", "unknown")
                status_color = {
                    "success": "green",
                    "warning": "yellow",
                    "error": "red",
                    "blocked": "red",
                }.get(status, "white")

                console.print(f"\n[bold {status_color}]Validation Status:[/bold {status_color}] {status}")

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}", err=True)
            sys.exit(1)

    asyncio.run(run())


@app.command()
def validate(
    ir_file: str = typer.Argument(..., help="Path to IR JSON file"),
):
    """Validate IR JSON schema."""
    console.print(f"[bold green]Validating IR:[/bold green] {ir_file}")

    try:
        with open(ir_file, "r") as f:
            ir_data = json.load(f)

        validator = IRValidator()
        is_valid, errors, repaired_ir = validator.validate(ir_data)

        if is_valid:
            console.print("[green]✓ IR is valid[/green]")
        else:
            console.print("[red]✗ IR validation failed:[/red]")
            for error in errors or []:
                console.print(f"  - {error}")

            if repaired_ir:
                repair_file = ir_file.replace(".json", "_repaired.json")
                with open(repair_file, "w") as f:
                    json.dump(repaired_ir, f, indent=2)
                console.print(f"[yellow]Repaired IR saved to:[/yellow] {repair_file}")

            sys.exit(1)

    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] File not found: {ir_file}", err=True)
        sys.exit(1)
    except json.JSONDecodeError as e:
        console.print(f"[bold red]Error:[/bold red] Invalid JSON: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}", err=True)
        sys.exit(1)


@app.command()
def optimize(
    ir_file: str = typer.Argument(..., help="Path to IR JSON file"),
    budget: int = typer.Option(4000, "--budget", "-b", help="Token budget"),
    intent: str = typer.Option("scaffold", "--intent", "-i", help="Intent for adaptive budgeting"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """Optimize IR JSON for token budget."""
    console.print(f"[bold green]Optimizing IR:[/bold green] {ir_file}")

    try:
        with open(ir_file, "r") as f:
            ir_data = json.load(f)

        optimizer = TokenOptimizer()
        optimized_ir, warnings = optimizer.optimize(ir_data, token_budget=budget, intent=intent)

        if warnings:
            console.print("[bold yellow]Warnings:[/bold yellow]")
            for warning in warnings:
                console.print(f"  - {warning}")

        if output_file:
            with open(output_file, "w") as f:
                json.dump(optimized_ir, f, indent=2)
            console.print(f"[green]Optimized IR saved to:[/green] {output_file}")
        else:
            console.print("[bold]Optimized IR:[/bold]")
            console.print(JSON(json.dumps(optimized_ir, indent=2)))

    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] File not found: {ir_file}", err=True)
        sys.exit(1)
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}", err=True)
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}", err=True)
        sys.exit(1)


@app.command()
def cache(
    command: str = typer.Argument(..., help="Command: stats or clear"),
):
    """Cache management commands."""
    cache_manager = CacheManager()

    if command == "stats":
        stats = cache_manager.stats()

        table = Table(title="Cache Statistics")
        table.add_column("Cache", style="cyan")
        table.add_column("Metric", style="magenta")
        table.add_column("Value", style="green")

        l1_stats = stats.get("l1", {})
        table.add_row("L1 (In-memory)", "Size", str(l1_stats.get("size", 0)))
        table.add_row("L1 (In-memory)", "Max Size", str(l1_stats.get("max_size", 0)))
        table.add_row("L1 (In-memory)", "TTL (seconds)", str(l1_stats.get("ttl_seconds", 0)))

        l2_stats = stats.get("l2", {})
        enabled = "Yes" if l2_stats.get("enabled") else "No"
        table.add_row("L2 (Redis)", "Enabled", enabled)
        if l2_stats.get("enabled"):
            table.add_row("L2 (Redis)", "Keys", str(l2_stats.get("keys", 0)))
            table.add_row("L2 (Redis)", "TTL (seconds)", str(l2_stats.get("ttl_seconds", 0)))

        console.print(table)

    elif command == "clear":
        cache_manager.clear()
        console.print("[green]Cache cleared[/green]")

    else:
        console.print(f"[bold red]Error:[/bold red] Unknown command: {command}", err=True)
        console.print("Available commands: stats, clear")
        sys.exit(1)


if __name__ == "__main__":
    app()
