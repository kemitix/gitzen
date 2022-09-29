from typing import Dict, List

from gitzen import config, console, git, repo_commit_stack
from gitzen.models.git_commit import GitCommit
from gitzen.types import GitBranchName


def scan(
    console_env: console.Env,
    git_env: git.Env,
    cfg: config.Config,
) -> Dict[GitBranchName, List[GitCommit]]:
    """
    Scans git log for commits for each branch in cfg, default and all remotes,
    back to their upstream origins.
    """
    result = {}
    branches = cfg.remote_branches
    branches.append(cfg.default_branch)
    remote = cfg.remote
    remote_branch = cfg.default_branch
    for branch in branches:
        git.switch(git_env, branch)
        stack = repo_commit_stack.get_commit_stack(
            console_env,
            git_env,
            remote,
            remote_branch,
        )
        result[branch] = stack
    return result
