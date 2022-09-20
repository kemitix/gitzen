import re
from typing import List, Tuple

from gitzen import console, envs, exit_code, git, patterns, zen_token
from gitzen.console import info
from gitzen.models.git_commit import GitCommit
from gitzen.types import (
    CommitBody,
    CommitHash,
    CommitTitle,
    CommitWipStatus,
    GitBranchName,
    GitRemoteName,
)


def get_local_branch_name(
    console_env: console.Env,
    git_env: git.GitEnv,
) -> GitBranchName:
    branches = git.branch(console_env, git_env)
    for branch in branches:
        # TODO detected detached HEAD
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
    git_env: envs.GitEnv,
    remote: GitRemoteName,
    remote_branch: GitBranchName,
) -> List[GitCommit]:
    log = git.log(
        console_env,
        git_env,
        f"{remote.value}/{remote_branch.value}..HEAD",
    )
    have_hash = False
    commits: List[GitCommit] = []
    hash = CommitHash("")
    headline = ""
    body: str = ""
    line_number = 0
    subject_index = 0
    for line in log:
        line_number += 1
        commit_matches = re.search(patterns.commit_log_hash, line)
        if commit_matches:
            if have_hash:
                info(
                    console_env,
                    "No zen-token found - is pre-commit hook installed?",
                )
                exit(exit_code.ZEN_TOKENS_MISSING)
            hash = CommitHash(commit_matches.group(1))
            info(console_env, f":: hash: {hash.value}")
            have_hash = True
            subject_index = line_number + 4
            continue
        token = zen_token.find_in_line(line[4:])
        if token is not None:
            info(console_env, f":: zen-token: {token.value}")
            info(console_env, f":: body: {body.strip()}")
            commits.append(
                GitCommit(
                    zen_token=token,
                    hash=hash,
                    headline=CommitTitle(headline),
                    body=CommitBody(body.strip()),
                    wip=CommitWipStatus(headline.startswith("WIP ")),
                )
            )
            body = ""
            have_hash = False
            continue
        if have_hash:
            if line_number == subject_index:
                headline = line.strip()
                info(console_env, f":: title: {headline}")
            elif line_number == (subject_index + 1) and line != "\n":
                body += line.strip() + "\n"
            elif line_number > (subject_index + 1):
                body += line.strip() + "\n"
    commits.reverse()
    return commits
