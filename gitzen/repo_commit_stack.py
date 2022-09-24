import re
from typing import List, Optional

from gitzen import console, git, patterns, zen_token
from gitzen.models.git_commit import GitCommit
from gitzen.types import (
    CommitBody,
    CommitHash,
    CommitTitle,
    CommitWipStatus,
    GitBranchName,
    GitRemoteName,
    ZenToken,
)


def get_commit_stack(
    console_env: console.Env,
    git_env: git.Env,
    remote: GitRemoteName,
    remote_branch: GitBranchName,
) -> List[GitCommit]:
    log = git.log(git_env, f"{remote.value}/{remote_branch.value}..HEAD")
    return parse_log_for_commits(console_env, log)


def parse_log_for_commits(
    console_env: console.Env,
    log: List[str],
) -> List[GitCommit]:
    if len(log) == 0:
        return []
    console.log(
        console_env,
        "parse-commit",
        f"Scanning {len(log)} log lines for commit...",
    )
    token: Optional[ZenToken] = None
    hash: Optional[CommitHash] = None
    headline: Optional[CommitTitle] = None
    body: str = ""
    line_number = -1
    subject_index = 0
    for line in log:
        line_number += 1
        commit_matches = re.search(patterns.commit_log_hash, line)
        if commit_matches:
            console.log(
                console_env,
                "parse-commit",
                f"Found commit hash: {commit_matches.group(1)}",
            )
            if token and hash and headline:
                commit = GitCommit(
                    zen_token=token,
                    hash=hash,
                    headline=headline,
                    body=CommitBody(body.strip()),
                    wip=CommitWipStatus(headline.value.startswith("WIP ")),
                )
                console.log(
                    console_env,
                    "parse-commit",
                    f"Completed commit: {commit}",
                )
                commits = parse_log_for_commits(
                    console_env,
                    log[line_number:],
                )
                commits.append(commit)
                return commits
            hash = CommitHash(commit_matches.group(1))
            subject_index = line_number + 4
            continue
        if token is None:
            token = zen_token.find_in_line(line[4:])
            if token:
                console.log(
                    console_env,
                    "parse-commit",
                    f"Found zen-token: {token.value}",
                )
        if hash:
            if line_number == subject_index:
                headline = CommitTitle(line.strip())
                console.log(
                    console_env,
                    "parse-commit",
                    f"Found commit title: {headline.value}",
                )
            elif line_number == (subject_index + 1) and line != "\n":
                body += line.strip() + "\n"
            elif line_number > (subject_index + 1):
                body += line.strip() + "\n"
    commits = []
    if token and hash and headline and body:
        commit = GitCommit(
            zen_token=token,
            hash=hash,
            headline=headline,
            body=CommitBody(body.strip()),
            wip=CommitWipStatus(headline.value.startswith("WIP ")),
        )
        console.log(
            console_env,
            "parse-commit",
            f"Completed final commit: {commit}",
        )
        commits.append(commit)
    return commits
