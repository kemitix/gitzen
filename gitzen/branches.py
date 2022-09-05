import re

from gitzen import config, exit_code


# look for the local branch name in the remote branches from config
# if found use that, otherwise, use the default branch from Config
def get_remote_branch(local_branch: str, config: config.Config) -> str:
    for remote_branch in config.remote_branches:
        if remote_branch == local_branch:
            return remote_branch
    return config.default_remote_branch


def get_required_remote_branch(
    local_branch: str,
    config: config.Config,
) -> str:
    remote_branch = get_remote_branch(local_branch, config)
    if len(remote_branch) == 0:
        print("remote branch not found")
        exit(exit_code.REMOTE_BRANCH_NOT_FOUND)
    return remote_branch


def validate_not_remote_pr(local_branch: str) -> None:
    matches = re.search(
        # gitzen/pr/{user}/{target-branch}/{zentoken}
        r"gitzen/pr/[a-zA-Z0-9_\-]+/([a-zA-Z0-9_\-/\.]+)/([a-f0-9]{8})$",
        local_branch,
    )
    if matches:
        print(
            "It looks like you've checked out the remote branch. "
            "You don't need to do that. "
            "Simply update your own local branch. "
            "Then use `git zen push` to update the pull request."
        )
        exit(exit_code.REMOTE_PR_CHECKED_OUT)
