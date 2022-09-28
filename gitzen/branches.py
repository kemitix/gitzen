import re

from gitzen import config, console, exit_code, patterns
from gitzen.console import info
from gitzen.models.github_pull_request import PullRequest
from gitzen.types import GitBranchName, GithubUsername, ZenToken


# look for the local branch name in the remote branches from config
# if found use that, otherwise, use the default branch from Config
def get_remote_branch(
    local_branch: GitBranchName,
    cfg: config.Config,
) -> GitBranchName:
    for remote_branch in cfg.remote_branches:
        if remote_branch == local_branch:
            return remote_branch
    return cfg.default_branch


def get_required_remote_branch(
    console_env: console.Env,
    local_branch: GitBranchName,
    cfg: config.Config,
) -> GitBranchName:
    remote_branch = get_remote_branch(local_branch, cfg)
    if len(remote_branch.value) == 0:
        info(console_env, "remote branch not found")
        exit(exit_code.REMOTE_BRANCH_NOT_FOUND)
    return remote_branch


def validate_not_remote_pr(
    console_env: console.Env,
    local_branch: GitBranchName,
) -> None:
    matches = re.search(patterns.remote_pr_branch, local_branch.value)
    if matches:
        info(
            console_env,
            "It looks like you've checked out the remote branch. "
            "You don't need to do that. "
            "Simply update your own local branch. "
            "Then use `git zen push` to update the pull request.",
        )
        exit(exit_code.REMOTE_PR_CHECKED_OUT)


def pr_branch(pr: PullRequest) -> GitBranchName:
    return pr_branch_spec(pr.author, pr.zen_token)


def pr_branch_spec(
    author: GithubUsername,
    zen_token: ZenToken,
) -> GitBranchName:
    return GitBranchName(f"gitzen/pr/{author.value}/{zen_token.value}")
