import re
from os import error
from typing import Tuple

from gitzen import git


def localBranch() -> str:
    branches = git.branch()
    for branch in branches:
        if branch.startswith("* "):
            return branch[2:]
    error("Can't find local branch name")
    exit


def getRepoDetailsFromRemote(remote: str) -> Tuple[str, str, str, bool]:
    # Allows "https://", "ssh://" or no protocol at all (this means ssh)
    protocolFormat = "(?:(https://)|(ssh://))?"
    # This may or may not be present in the address
    userFormat = "(git@)?"
    # "/" is expected in "http://" or "ssh://" protocol, when no protocol given
    # it should be ":"
    repoFormat = (
        r"(?P<githubHost>[a-z0-9._\-]+)(/|:)"
        r"(?P<repoOwner>\w+)/"
        r"(?P<repoName>[\w-]+)"
    )
    # This is neither required in https access nor in ssh one
    suffixFormat = "(.git)?"
    regexFormat = r"^origin\s+%s%s%s%s \(push\)" % (
        protocolFormat,
        userFormat,
        repoFormat,
        suffixFormat,
    )
    regex = re.compile(regexFormat)
    match = regex.search(remote)
    if match:
        githubHost = match.group("githubHost")
        repoOwner = match.group("repoOwner")
        repoName = match.group("repoName")
        return githubHost, repoOwner, repoName, True
    return "", "", "", False
