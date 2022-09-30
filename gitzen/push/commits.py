from gitzen import config, console, git, repo_commit_stack
from gitzen.models.stack import Stack


def scan(
    console_env: console.Env,
    git_env: git.Env,
    cfg: config.Config,
) -> Stack:
    """
    Scans git log for commits for each branch in cfg, default and all remotes,
    back to their upstream origins.
    """
    branches = {}
    heads = cfg.remote_branches
    heads.append(cfg.default_branch)
    remote = cfg.remote
    remote_branch = cfg.default_branch
    for branch in heads:
        git.switch(git_env, branch)
        stack = repo_commit_stack.get_commit_stack(
            console_env,
            git_env,
            remote,
            remote_branch,
        )
        branches[branch] = stack
    return Stack(branches=branches)
