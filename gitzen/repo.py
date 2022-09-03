import re
from typing import Tuple

from gitzen import exit_code, git


# will exit the program if called from outside a git repo
def root_dir(git_env: git.GitEnv) -> str:
    output = git.rev_parse(git_env, "--show-toplevel")
    if output == "":
        exit(exit_code.NOT_IN_GIT_REPO)
    return output[0]


def get_local_branch_name(git_env: git.GitEnv) -> str:
    branches = git.branch(git_env)
    for branch in branches:
        # TODO detected detached HEAD
        if branch.startswith("* "):
            return branch[2:]
    print("ERROR: Can't find local branch name")
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
