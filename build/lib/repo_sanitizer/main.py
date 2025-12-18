import typer
from rich.console import Console
from rich.markdown import Markdown

from repo_sanitizer.git_handler import (
    load_repo,
    fetch_and_prune,
    get_local_branches,
)
from repo_sanitizer.analyzer import find_stale
from repo_sanitizer.ui import select, print_summary
from repo_sanitizer.logger import log
from repo_sanitizer.config import load_config
from repo_sanitizer.undo import restore

app = typer.Typer()
console = Console()
cfg = load_config()


@app.command()
def clean(
    dry_run: bool = typer.Option(False),
    all: bool = typer.Option(False),
    explain: bool = typer.Option(False, "--explain", help="Explain stale branches using AI"),
):
    repo = load_repo()
    fetch_and_prune(repo)

    stale = find_stale(repo, get_local_branches(repo))

    if not stale:
        console.print("[green]No stale branches found[/green]")
        return

    if explain:
        from repo_sanitizer.ai_explainer import explain_branch
        from repo_sanitizer.git_handler import get_branch_metadata

        for b in stale:
            try:
                info = get_branch_metadata(repo, b)
                info["merged"] = True  # already verified by analyzer
                explanation = explain_branch(info)
                console.print(f"\n[bold cyan]🔍 Analysis for {b}:[/bold cyan]")
                console.print(Markdown(explanation))
                console.print()
            except Exception as e:
                console.print(f"[yellow]AI skipped for {b}: {e}[/yellow]")

    if dry_run or cfg["dry_run_default"]:
        for b in stale:
            console.print(f"[yellow]DRY RUN → {b}[/yellow]")
        return

    selected = stale if all or cfg["auto_confirm"] else select(stale)

    if not selected:
        console.print("[yellow]Nothing selected[/yellow]")
        return

    print_summary(repo, selected)


@app.command()
def undo(branch: str):
    repo = load_repo()
    restore(repo, branch)
    console.print(f"[green]Restored {branch}[/green]")


@app.command()
def push(
    auto: bool = typer.Option(False, "--auto", "-a", help="Skip confirmation"),
):
    """Stage all changes, generate an AI commit message, commit, and push."""
    repo = load_repo()

    from repo_sanitizer.git_handler import (
        stage_all_changes,
        get_staged_diff,
        commit_changes,
        push_changes,
    )
    from repo_sanitizer.ai_explainer import generate_commit_message

    # 1. Stage everything to see what we are working with
    stage_all_changes(repo)

    # 2. Get diff
    diff = get_staged_diff(repo)

    if not diff:
        console.print("[yellow]No changes to commit.[/yellow]")
        return

    # 3. Generate message
    with console.status("[bold green]🤖 Generating commit message...[/bold green]"):
        msg = generate_commit_message(diff)

    console.print(f"\n[bold cyan]📝 Proposed Commit Message:[/bold cyan]")
    console.print(f"[white]{msg}[/white]\n")

    # 4. Confirm
    if not auto:
        if not typer.confirm("🚀 Commit and push?"):
            console.print("[red]Aborted.[/red]")
            raise typer.Abort()

    # 5. Commit and Push
    try:
        commit_changes(repo, msg)
        console.print("[green]✓ Committed[/green]")

        with console.status("[bold green]Pushing to remote...[/bold green]"):
            push_changes(repo)

        console.print("[bold green]✨ Successfully pushed![/bold green]")
    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")
