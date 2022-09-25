import re
from typing import List, Tuple

from gitzen import console, exit_code, git, repo_commit_stack
from gitzen.console import info
from gitzen.models.git_commit import GitCommit
from gitzen.types import GitBranchName, GitRemoteName


def get_local_branch_name(
    console_env: console.Env,
    git_env: git.Env,
) -> GitBranchName:
    branches = git.branch(git_env)[1]
    for branch in branches:
        # TODO detect detached HEAD
        if branch.startswith("* "):
            return GitBranchName(branch[2:])
    info(console_env, "ERROR: Can't find local branch name")
    exit(exit_code.NO_LOCAL_BRANCH_FOUND)


def get_repo_details_from_remote(remote: str) -> Tuple[str, str, str, bool]:
    # Allows "https://", "ssh://" or no protocol at all (this means ssh)
    protocol_format = "(?:(https://)|(ssh://))?"
    # This may or may not be present in the address
    user_format = "(git@)?"
    # "/" is expected in "http://" or "ssh://" protocol, when no protocol given
    # it should be ":"
    repo_format = (
        r"(?P<githubHost>[a-z0-9._\-]+)(/|:)"
        r"(?P<repoOwner>\w+)/"
        r"(?P<repoName>[\w-]+)"
    )
    # This is neither required in https access nor in ssh one
    suffix_format = "(.git)?"
    regex_format = r"^origin\s+%s%s%s%s \(push\)" % (
        protocol_format,
        user_format,
        repo_format,
        suffix_format,
    )
    regex = re.compile(regex_format)
    match = regex.search(remote)
    if match:
        github_host = match.group("githubHost")
        repo_owner = match.group("repoOwner")
        repo_name = match.group("repoName")
        return github_host, repo_owner, repo_name, True
    return "", "", "", False


def get_commit_stack(
    console_env: console.Env,
    git_env: git.Env,
    remote: GitRemoteName,
    remote_branch: GitBranchName,
) -> List[GitCommit]:
    return repo_commit_stack.get_commit_stack(
        console_env,
        git_env,
        remote,
        remote_branch,
    )
