import typer
from rich import print
from git_handler import load_repo, get_local_branches, fetch_and_prune
from analyzer import find_stale_branches
from ui import choose_branches_to_delete, print_summary


app = typer.Typer(no_args_is_help=True)


@app.command()
def clean(force: bool = typer.Option(False, "--force", "-f", help="Delete without confirmation")):
    """Clean stale branches from your local git repo."""
    
    repo = load_repo()
    fetch_and_prune(repo)

    local_branches = get_local_branches(repo)
    stale = find_stale_branches(repo, local_branches)

    if not stale:
        print("[green]✨ No stale branches found! Clean repo![/green]")
        return

    if force:
        to_delete = stale
    else:
        to_delete = choose_branches_to_delete(stale)

    print_summary(repo, to_delete)


if __name__ == "__main__":
    app()
