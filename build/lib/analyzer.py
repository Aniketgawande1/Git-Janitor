from rich import print
from git_handler import get_upstream_status


PROTECTED = {"main", "master", "dev", "develop"}


def is_protected(name: str):
    return name in PROTECTED


def is_merged_into_main(repo, branch_name: str):
    """Check if branch was merged into main."""
    if "main" not in repo.heads:
        return False

    main_commit = repo.heads["main"].commit
    branch_commit = repo.heads[branch_name].commit

    # If ancestor, branch is merged
    return repo.git.merge_base(main_commit, branch_commit) == repo.git.rev_parse(branch_commit)


def find_stale_branches(repo, local_branches):
    stale = []

    for branch in local_branches:
        if is_protected(branch):
            continue

        upstream = get_upstream_status(repo, branch)
        if upstream == "gone":
            stale.append(branch)
            continue

        if is_merged_into_main(repo, branch):
            stale.append(branch)
            continue

    return stale
