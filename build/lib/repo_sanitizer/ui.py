from InquirerPy import inquirer
from rich import print
from rich.table import Table


def choose_branches_to_delete(stale_branches):
    """Interactive selection of branches to delete."""
    table = Table(title="Stale Branches Detected")
    table.add_column("Branch")
    for b in stale_branches:
        table.add_row(b)

    print(table)

    selected = inquirer.checkbox(
        message="Select branches to delete:",
        choices=stale_branches,
    ).execute()

    return selected


def print_summary(repo, branches_to_delete):
    print()
    print("[yellow]🗑️ Deleting selected branches...[/yellow]")

    for b in branches_to_delete:
        try:
            repo.git.branch("-D", b)
            print(f"[green]✓ Deleted {b}[/green]")
        except Exception as e:
            print(f"[red]✗ Failed to delete {b}: {e}[/red]")

    print("\n[bold green]✨ Cleanup complete![/bold green]")
