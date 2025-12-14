from git import Repo, InvalidGitRepositoryError
from rich import print
import typer


def load_repo():
    """Load the git repo in the current directory."""
    try:
        repo = Repo(".", search_parent_directories=True)
        return repo
    except InvalidGitRepositoryError:
        print("[red]❌ Not a git repository.[/red]")
        raise typer.Exit()


def fetch_and_prune(repo: Repo):
    """Fetch remote branches and remove stale tracking refs."""
    print("[yellow]🔄 Fetching and pruning remote branches...[/yellow]")
    repo.git.fetch("--prune")


def get_local_branches(repo: Repo):
    """Return all local branch names."""
    return [h.name for h in repo.heads]


def get_upstream_status(repo: Repo, branch_name: str):
    """Return upstream status: exists or gone."""
    branch = repo.heads[branch_name]

    upstream = branch.tracking_branch()
    if upstream is None:
        return "no-upstream"

    try:
        repo.git.rev_parse(upstream.name)
        return "exists"
    except Exception:
        return "gone"
