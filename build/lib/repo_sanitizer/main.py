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


@app.command()
def review():
    """AI Code Review for your current working changes."""
    repo = load_repo()
    from repo_sanitizer.git_handler import get_working_tree_diff, get_staged_diff
    from repo_sanitizer.ai_explainer import generate_code_review

    # Check both staged and unstaged changes
    diff = get_staged_diff(repo) + "\n" + get_working_tree_diff(repo)
    
    if not diff.strip():
        console.print("[yellow]No changes to review.[/yellow]")
        return

    with console.status("[bold cyan]🤖 Analyzing code...[/bold cyan]"):
        review = generate_code_review(diff)

    console.print("\n[bold magenta]🧐 AI Code Review:[/bold magenta]")
    console.print(Markdown(review))
    console.print()


@app.command()
def summary(limit: int = typer.Option(10, "--limit", "-n", help="Number of commits to summarize")):
    """AI Summary of recent commit history."""
    repo = load_repo()
    from repo_sanitizer.git_handler import get_commit_history
    from repo_sanitizer.ai_explainer import summarize_history

    commits = get_commit_history(repo, limit)
    
    if not commits:
        console.print("[yellow]No commits found.[/yellow]")
        return

    with console.status("[bold green]📊 Summarizing history...[/bold green]"):
        summary = summarize_history(commits)

    console.print("\n[bold blue]📜 Project Activity Summary:[/bold blue]")
    console.print(Markdown(summary))
    console.print()


@app.command()
def merge(branch: str):
    """Merge a branch with AI summary of incoming changes."""
    repo = load_repo()
    from repo_sanitizer.git_handler import get_incoming_commits, merge_branch
    from repo_sanitizer.ai_explainer import summarize_history

    commits = get_incoming_commits(repo, branch)
    
    if not commits:
        console.print(f"[yellow]No new commits in {branch} to merge.[/yellow]")
        return

    console.print(f"[bold cyan]🔍 Analyzing {len(commits)} incoming commits from {branch}...[/bold cyan]")
    
    with console.status("[bold green]🤖 Generating summary...[/bold green]"):
        summary = summarize_history(commits)

    console.print("\n[bold magenta]Incoming Changes Summary:[/bold magenta]")
    console.print(Markdown(summary))
    console.print()

    if typer.confirm(f"🚀 Merge {branch} into current branch?"):
        try:
            merge_branch(repo, branch)
            console.print(f"[green]✓ Successfully merged {branch}[/green]")
        except Exception as e:
            console.print(f"[red]✗ Merge failed: {e}[/red]")
    else:
        console.print("[yellow]Merge aborted.[/yellow]")


@app.command()
def pull():
    """Pull upstream changes with AI summary."""
    repo = load_repo()
    from repo_sanitizer.git_handler import fetch_repo, get_commits_behind, pull_changes
    from repo_sanitizer.ai_explainer import summarize_history

    with console.status("[bold blue]🔄 Fetching updates...[/bold blue]"):
        fetch_repo(repo)
    
    commits = get_commits_behind(repo)
    
    if not commits:
        console.print("[green]Already up to date![/green]")
        return

    console.print(f"[bold cyan]🔍 Found {len(commits)} new commits upstream...[/bold cyan]")
    
    with console.status("[bold green]🤖 Generating summary...[/bold green]"):
        summary = summarize_history(commits)

    console.print("\n[bold magenta]Upstream Updates Summary:[/bold magenta]")
    console.print(Markdown(summary))
    console.print()

    if typer.confirm("🚀 Pull updates?"):
        try:
            pull_changes(repo)
            console.print("[green]✓ Successfully pulled updates[/green]")
        except Exception as e:
            console.print(f"[red]✗ Pull failed: {e}[/red]")
    else:
        console.print("[yellow]Pull aborted.[/yellow]")


@app.command()
def rebase(branch: str):
    """Rebase onto a branch with AI summary."""
    repo = load_repo()
    from repo_sanitizer.git_handler import get_incoming_commits, rebase_branch
    from repo_sanitizer.ai_explainer import summarize_history

    commits = get_incoming_commits(repo, branch)
    
    if not commits:
        console.print(f"[yellow]No new commits in {branch} to rebase onto.[/yellow]")
        return

    console.print(f"[bold cyan]🔍 Analyzing {len(commits)} commits from {branch}...[/bold cyan]")
    
    with console.status("[bold green]🤖 Generating summary...[/bold green]"):
        summary = summarize_history(commits)

    console.print("\n[bold magenta]Rebase Target Summary:[/bold magenta]")
    console.print(Markdown(summary))
    console.print()

    if typer.confirm(f"🚀 Rebase onto {branch}?"):
        try:
            rebase_branch(repo, branch)
            console.print(f"[green]✓ Successfully rebased onto {branch}[/green]")
        except Exception as e:
            console.print(f"[red]✗ Rebase failed: {e}[/red]")
    else:
        console.print("[yellow]Rebase aborted.[/yellow]")
