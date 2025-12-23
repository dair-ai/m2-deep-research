#!/usr/bin/env python3
"""
Deep Research Agent CLI

A command-line interface for conducting deep research using:
- Minimax M2.1 (supervisor with interleaved thinking)
- Exa API (neural web search)
- OpenRouter (subagent LLMs)
"""

import sys
import os
import argparse
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich import print as rprint
from src.agents.supervisor import SupervisorAgent
from src.utils.config import Config

# Initialize rich console
console = Console()


def print_banner():
    """Print welcome banner with colors."""
    banner_text = Text()
    banner_text.append("DEEP RESEARCH AGENT", style="bold cyan")
    banner_text.append("\nPowered by ", style="white")
    banner_text.append("Minimax M2.1", style="bold magenta")
    banner_text.append(" with ", style="white")
    banner_text.append("Interleaved Thinking", style="bold green")

    console.print(Panel(
        banner_text,
        border_style="cyan",
        padding=(1, 2)
    ))


def print_section(title: str):
    """Print a formatted section header with colors."""
    console.print(f"\n[bold cyan]{'=' * 80}[/bold cyan]")
    console.print(f"[bold yellow] {title}[/bold yellow]")
    console.print(f"[bold cyan]{'=' * 80}[/bold cyan]")


def save_report(content: str, query: str):
    """Save research report to a file in the reports/ folder."""
    # Create reports directory if it doesn't exist
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Create a safe filename from query
    safe_query = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in query)
    safe_query = safe_query.strip()[:50]  # Limit length
    filename = f"research_report_{safe_query}_{timestamp}.md"
    filepath = os.path.join(reports_dir, filename)

    try:
        with open(filepath, 'w') as f:
            f.write(f"# Research Report\n\n")
            f.write(f"**Query:** {query}\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            f.write(content)

        console.print(f"\n[bold green]✓ Report saved to:[/bold green] [cyan]{filepath}[/cyan]")
        return filepath
    except Exception as e:
        console.print(f"\n[bold red]✗ Error saving report:[/bold red] {e}")
        return None


def run_research(query: str, verbose: bool = False, save: bool = False):
    """
    Run research for a given query.

    Args:
        query: Research question or topic
        verbose: Show detailed progress
        save: Save report to file
    """
    try:
        # Initialize supervisor
        if verbose:
            console.print("\n[dim]Initializing Minimax M2.1 Supervisor Agent...[/dim]")

        supervisor = SupervisorAgent()

        # Conduct research
        print_section("CONDUCTING RESEARCH")
        console.print(f"[bold white]Query:[/bold white] [italic cyan]{query}[/italic cyan]\n")

        if verbose:
            console.print("[dim]→ Planning research strategy...[/dim]")
            console.print("[dim]→ Searching web with Exa...[/dim]")
            console.print("[dim]→ Synthesizing findings...[/dim]\n")

        result = supervisor.research(query)

        # Display results
        print_section("RESEARCH REPORT")

        # Display markdown-formatted result with colors
        console.print(Markdown(result))
        console.print(f"\n[bold cyan]{'=' * 80}[/bold cyan]")

        # Save if requested
        if save:
            save_report(result, query)

        # Show thinking in verbose mode
        if verbose:
            print_section("CONVERSATION HISTORY (VERBOSE)")
            history = supervisor.get_conversation_history()
            for i, msg in enumerate(history, 1):
                console.print(f"\n[bold magenta]--- Message {i} ({msg['role']}) ---[/bold magenta]")
                if isinstance(msg['content'], list):
                    for block in msg['content']:
                        if hasattr(block, 'type'):
                            console.print(f"[cyan]  Block type: {block.type}[/cyan]")
                            if block.type == "thinking":
                                console.print(f"[dim]  Thinking: {block.thinking[:200]}...[/dim]")
                            elif block.type == "text":
                                console.print(f"[white]  Text: {block.text[:200]}...[/white]")
                else:
                    console.print(f"[white]  Content: {str(msg['content'])[:200]}...[/white]")

    except Exception as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {e}")
        sys.exit(1)


def interactive_mode():
    """Run in interactive mode with multiple queries."""
    print_banner()
    console.print("\n[bold cyan]Interactive mode[/bold cyan] - Enter your research queries (type [yellow]'exit'[/yellow] to quit)\n")

    while True:
        try:
            query = input("\n🔍 Research Query: ").strip()

            if not query:
                continue

            if query.lower() in ['exit', 'quit', 'q']:
                console.print("\n[bold green]👋 Goodbye![/bold green]")
                break

            # Check for special commands
            save = False
            verbose = False

            if query.startswith('/'):
                if query.startswith('/save '):
                    save = True
                    query = query[6:].strip()
                elif query.startswith('/verbose '):
                    verbose = True
                    query = query[9:].strip()
                elif query == '/help':
                    console.print("\n[bold yellow]Commands:[/bold yellow]")
                    console.print("  [cyan]/save <query>[/cyan]     - Save report to file")
                    console.print("  [cyan]/verbose <query>[/cyan]  - Show detailed progress")
                    console.print("  [cyan]/help[/cyan]             - Show this help")
                    console.print("  [cyan]exit/quit/q[/cyan]       - Exit")
                    continue

            run_research(query, verbose=verbose, save=save)

        except KeyboardInterrupt:
            console.print("\n\n[bold green]👋 Goodbye![/bold green]")
            break
        except Exception as e:
            console.print(f"\n[bold red]✗ Error:[/bold red] {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Deep Research Agent - Conduct thorough research using Minimax M2.1 and Exa",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python main.py

  # Single query
  python main.py -q "What are the latest developments in quantum computing?"

  # Save report to file
  python main.py -q "AI trends in 2025" --save

  # Verbose mode with thinking details
  python main.py -q "Climate change solutions" --verbose
        """
    )

    parser.add_argument(
        '-q', '--query',
        type=str,
        help='Research query (if not provided, runs in interactive mode)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed progress and thinking blocks'
    )

    parser.add_argument(
        '-s', '--save',
        action='store_true',
        help='Save research report to file'
    )

    args = parser.parse_args()

    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        console.print(f"[bold red]✗ Configuration Error:[/bold red] {e}")
        console.print("\n[yellow]Please ensure you have:[/yellow]")
        console.print("[dim]1. Copied .env.example to .env[/dim]")
        console.print("[dim]2. Added your API keys to .env[/dim]")
        sys.exit(1)

    # Run mode based on arguments
    if args.query:
        # Single query mode
        print_banner()
        run_research(args.query, verbose=args.verbose, save=args.save)
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
