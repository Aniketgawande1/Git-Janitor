def restore(repo, branch):
    sha = repo.git.reflog("--format=%H", "-n", "1", branch)
    repo.git.branch(branch, sha)
