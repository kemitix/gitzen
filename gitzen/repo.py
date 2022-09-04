import re
from typing import List, Tuple

from gitzen import envs, exit_code, git
from gitzen.models.github_commit import Commit


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


def get_commit_stack(
    git_env: envs.GitEnv,
    remote: str,
    remote_branch: str,
) -> List[Commit]:
    log = git.log(git_env, f"{remote}/{remote_branch}..HEAD")
    have_hash = False
    commits: List[Commit] = []
    hash = ""
    headline = ""
    body = ""
    line_number = 0
    subject_index = 0
    for line in log:
        line_number += 1
        commit_matches = re.search("^commit ([a-f0-9]{40})", line)
        if commit_matches:
            if have_hash:
                print("No zen-token found - is pre-commit hook installed?")
                exit(exit_code.ZEN_TOKENS_MISSING)
            hash = commit_matches.group(1)
            have_hash = True
            subject_index = line_number + 4
            continue
        zen_token_matches = re.search("zen-token:([a-f0-9]{8})", line)
        if zen_token_matches:
            commits.append(
                Commit(
                    zen_token=zen_token_matches.group(1),
                    hash=hash,
                    headline=headline,
                    body=body.strip(),
                    wip=headline.startswith("WIP "),
                )
            )
            body = ""
            have_hash = False
            continue
        if have_hash:
            if line_number == subject_index:
                headline = line.strip()
            elif line_number == (subject_index + 1) and line != "\n":
                body += line.strip() + "\n"
            elif line_number > (subject_index + 1):
                body += line.strip() + "\n"
    commits.reverse()
    return commits
