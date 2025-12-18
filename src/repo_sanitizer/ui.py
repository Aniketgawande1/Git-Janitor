from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from rich import print
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from rich.theme import Theme
from .logger import log

console = Console(
    theme=Theme({
        "title": "bold cyan",
        "branch": "bold yellow",
        "danger": "bold red",
        "success": "bold green",
        "info": "bold blue",
    })
)


def show_header():
    console.print(Panel.fit(
        "[bold cyan]🚀 Repo-Sanitizer[/bold cyan]\n"
        "[green]Clean stale branches safely & fast[/green]",
        title="[bold magenta]🔥 Branch Cleaner UI 🔥[/bold magenta]",
        subtitle="[yellow]Made by Aniket[/yellow]",
        border_style="bright_blue",
    ))


def select(stale_branches):
    """Show a beautiful color table + selection menu."""
    
    show_header()

    # table of stale branches
    table = Table(
        title="[bold cyan]Stale Branches Detected[/bold cyan]",
        header_style="bold blue",
        border_style="bright_magenta"
    )
    table.add_column("Branch Name", justify="center", style="branch")

    for b in stale_branches:
        table.add_row(f"[branch]{b}[/branch]")

    console.print(table)

    console.print("\n[bold yellow]👇 Select branches to delete:[/bold yellow]\n")

    choices = [Choice(b, enabled=True) for b in stale_branches]

    selected = inquirer.checkbox(
        message="✔ Choose branches (use SPACE to select):",
        choices=choices,
        instruction="Use ↑↓ arrows to navigate",
    ).execute()

    return selected


def print_summary(repo, branches_to_delete):
    console.print("\n[yellow]🗑️ Deleting selected branches...[/yellow]\n")

    for b in branches_to_delete:
        try:
            repo.git.branch("-D", b)
            log.info(f"Deleted {b}")
            console.print(f"[success]✓ Deleted[/success] [bold]{b}[/bold]")
        except Exception as e:
            console.print(f"[danger]✗ Failed to delete {b}[/danger] → {e}")

    console.print("\n[bold green]✨ Cleanup complete![/bold green]")
