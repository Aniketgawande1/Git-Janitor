from git import Repo, InvalidGitRepositoryError
from pathlib import Path
import typer

def load_repo():
    try:
        return Repo(Path.cwd(), search_parent_directories=False)
    except InvalidGitRepositoryError:
        raise typer.Exit("❌ Not a Git repository")

def fetch_and_prune(repo):
    try:
        repo.git.fetch("--prune")
    except Exception:
        pass

def get_local_branches(repo):
    return [b.name for b in repo.branches]

def get_upstream_status(repo, branch):
    b = repo.branches[branch]
    upstream = b.tracking_branch()
    if not upstream:
        return "no-upstream"
    try:
        repo.git.rev_parse(upstream.name)
        return "exists"
    except Exception:
        return "gone"


def get_branch_metadata(repo, branch_name):
    commit = repo.heads[branch_name].commit
    return {
        "branch": branch_name,
        "last_commit_message": commit.message.strip(),
        "last_commit_date": commit.committed_datetime.isoformat(),
        "commit_count": repo.git.rev_list("--count", branch_name),
        "upstream_status": get_upstream_status(repo, branch_name)
    }


def stage_all_changes(repo):
    """Stage all changes (including untracked files)."""
    repo.git.add(".")


def get_staged_diff(repo):
    """Get diff of staged changes."""
    return repo.git.diff("--cached")


def commit_changes(repo, message):
    """Commit staged changes."""
    repo.index.commit(message)


def push_changes(repo):
    """Push current branch to upstream, setting it if missing."""
    active_branch = repo.active_branch
    if not active_branch.tracking_branch():
        repo.git.push("--set-upstream", "origin", active_branch.name)
    else:
        repo.git.push()


def get_working_tree_diff(repo):
    """Get diff of unstaged changes."""
    return repo.git.diff()


def get_commit_history(repo, limit=10):
    """Get recent commit history."""
    commits = list(repo.iter_commits(max_count=limit))
    return [{"hash": c.hexsha[:7], "message": c.message.strip(), "author": c.author.name, "date": c.committed_datetime.isoformat()} for c in commits]


def get_incoming_commits(repo, source_branch):
    """Get commits in source_branch that are not in HEAD."""
    try:
        commits = list(repo.iter_commits(f"HEAD..{source_branch}"))
        return [{"hash": c.hexsha[:7], "message": c.message.strip(), "author": c.author.name, "date": c.committed_datetime.isoformat()} for c in commits]
    except Exception:
        return []


def get_commits_behind(repo):
    """Get commits that upstream has but we don't."""
    try:
        commits = list(repo.iter_commits("HEAD..@{u}"))
        return [{"hash": c.hexsha[:7], "message": c.message.strip(), "author": c.author.name, "date": c.committed_datetime.isoformat()} for c in commits]
    except Exception:
        return []


def fetch_repo(repo):
    """Fetch updates from remote."""
    repo.git.fetch()


def merge_branch(repo, branch):
    """Merge a branch into the current branch."""
    repo.git.merge(branch)


def rebase_branch(repo, branch):
    """Rebase current branch onto another branch."""
    repo.git.rebase(branch)


def pull_changes(repo):
    """Pull changes from upstream."""
    repo.git.pull()
