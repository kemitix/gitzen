import re

from gitzen import config, envs, exit_code, patterns
from gitzen.console import say


# look for the local branch name in the remote branches from config
# if found use that, otherwise, use the default branch from Config
def get_remote_branch(local_branch: str, config: config.Config) -> str:
    for remote_branch in config.remote_branches:
        if remote_branch == local_branch:
            return remote_branch
    return config.default_remote_branch


def get_required_remote_branch(
    console_env: envs.ConsoleEnv,
    local_branch: str,
    config: config.Config,
) -> str:
    remote_branch = get_remote_branch(local_branch, config)
    if len(remote_branch) == 0:
        say(console_env, "remote branch not found")
        exit(exit_code.REMOTE_BRANCH_NOT_FOUND)
    return remote_branch


def validate_not_remote_pr(
    console_env: envs.ConsoleEnv,
    local_branch: str,
) -> None:
    matches = re.search(patterns.remote_branch, local_branch)
    if matches:
        say(
            console_env,
            "It looks like you've checked out the remote branch. "
            "You don't need to do that. "
            "Simply update your own local branch. "
            "Then use `git zen push` to update the pull request.",
        )
        exit(exit_code.REMOTE_PR_CHECKED_OUT)
