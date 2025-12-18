from concurrent.futures import ThreadPoolExecutor

from repo_sanitizer.git_handler import get_upstream_status
from repo_sanitizer.config import load_config

cfg = load_config()
PROTECTED = set(cfg["protected_branches"])


def is_protected(branch):
    return branch in PROTECTED


def base_branch(repo):
    for b in cfg["protected_branches"]:
        if b in repo.branches:
            return repo.branches[b]
    return None


def is_merged(repo, base, branch):
    merged = repo.git.branch("--merged", base.name)
    merged = [b.replace("*", "").strip() for b in merged.splitlines()]
    return branch in merged


def find_stale(repo, branches):
    base = base_branch(repo)
    stale = []

    def check(branch):
        if is_protected(branch):
            return None
        if get_upstream_status(repo, branch) == "gone":
            return branch
        if base and is_merged(repo, base, branch):
            return branch
        return None

    with ThreadPoolExecutor() as ex:
        for r in ex.map(check, branches):
            if r:
                stale.append(r)

    return stale
