import json
import re
import shlex
import subprocess
from typing import Any, Dict, List

from gitzen import console, git, github, patterns, repo, zen_token
from gitzen.models.git_commit import GitCommit
from gitzen.models.github_commit import GithubCommit
from gitzen.models.github_info import GithubInfo
from gitzen.models.github_pull_request import PullRequest
from gitzen.types import (
    CommitBody,
    CommitHash,
    CommitTitle,
    CommitWipStatus,
    GitBranchName,
    GithubRepoId,
    GithubUsername,
    PullRequestBody,
    PullRequestId,
    PullRequestMergeable,
    PullRequestNumber,
    PullRequestReviewDecision,
    PullRequestTitle,
)


class Env:
    def _graphql(
        self,
        console_env: console.Env,
        params: Dict[str, str],
        query: str,
    ) -> Dict[str, Any]:
        pass

    def _gh(
        self,
        console_env: console.Env,
        args: str,
    ) -> List[str]:
        pass


class RealEnv(github.Env):
    def _graphql(
        self,
        console_env: console.Env,
        params: Dict[str, str],
        query: str,
    ) -> Dict[str, Any]:
        cmd = "gh api graphql"
        args = shlex.split(cmd)
        console.log(console_env, "github", f"{cmd} ...")
        for pair in params:
            args.append("-F")
            args.append(f"{pair}=" + params[pair])
        args.append("-f")
        args.append(f"query={query}")
        result = subprocess.run(args, stdout=subprocess.PIPE)
        stdout = result.stdout
        if stdout:
            return json.loads(stdout.decode())
        else:
            return {}  # TODO return some error condition

    def _gh(self, console_env: console.Env, args: str) -> List[str]:
        console.log(console_env, "github", args)
        gh_command = shlex.split(f"gh {args}")
        result = subprocess.run(
            gh_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        stdout = result.stdout
        if stdout:
            lines = stdout.decode().splitlines()
            [console.log(console_env, "github", f"| {line}") for line in lines]
            console.log(console_env, "github", "\\------------------")
            return lines
        else:
            console.log(console_env, "github", "\\------------------")
            return []


# trunk-ignore(flake8/E501)
# GraphQL originally from https://github.com/ejoffe/spr/blob/9597afc52354db66d4b419f7ee7a9bd7eacdf70f/github/githubclient/gen/genclient/operations.go#L72
query_status = """query($repo_owner: String!, $repo_name: String!){
    viewer {
        login
        repository(name: $repo_name) {
            pullRequests(first: 100, states: [OPEN]) {
                nodes {
                    id
                    number
                    title
                    body
                    baseRefName
                    headRefName
                    mergeable
                    reviewDecision
                    repository {
                        id
                    }
                    commits(first: 100) {
                        nodes {
                            commit {
                                oid
                                messageHeadline
                                messageBody
                                statusCheckRollup {
                                    state
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    repository(owner: $repo_owner, name: $repo_name) {
        id
    }
}
"""


def fetch_info(
    console_env: console.Env,
    git_env: git.Env,
    github_env: Env,
) -> GithubInfo:
    data = github_env._graphql(
        console_env,
        {
            "repo_owner": "{owner}",
            "repo_name": "{repo}",
        },
        query_status,
    )["data"]
    repo_id = GithubRepoId(data["repository"]["id"])
    viewer = data["viewer"]
    pr_nodes = viewer["repository"]["pullRequests"]["nodes"]
    prs: List[PullRequest] = []
    console.info(console_env, f"Found {len(pr_nodes)} prs")
    for pr_node in pr_nodes:
        pr_repo_id = GithubRepoId(pr_node["repository"]["id"])
        if repo_id != pr_repo_id:
            continue
        base_ref = GitBranchName(pr_node["baseRefName"])
        head_ref = GitBranchName(pr_node["headRefName"])
        console.info(console_env, f"{base_ref.value} <- {head_ref.value}")
        match = re.search(patterns.remote_pr_branch, head_ref.value)
        if match is None:
            console.log(
                console_env,
                "github.fetch_info",
                "unknown head_ref: " + head_ref.value,
            )
            continue
        if match.group("target_branch") != base_ref.value:
            console.info(
                console_env,
                "ignore prs that don't target expected base branch",
            )
            continue
        review_node = pr_node["reviewDecision"]
        review_decision = PullRequestReviewDecision(
            review_node if review_node is not None else ""
        )
        body = PullRequestBody(pr_node["body"])
        token = zen_token.find_in_body(body)
        if token is None:
            continue
        commits = get_commits(pr_node)
        prs.append(
            PullRequest(
                PullRequestId(pr_node["id"]),
                token,
                PullRequestNumber(f'{pr_node["number"]}'),
                GithubUsername(viewer["login"]),
                PullRequestTitle(pr_node["title"]),
                body,
                base_ref,
                head_ref,
                commits[0].hash,
                PullRequestMergeable(pr_node["mergeable"]),
                review_decision,
                pr_repo_id,
                commits,
            )
        )
    console.info(console_env, f"Kept {len(prs)} prs")
    return GithubInfo(
        GithubUsername(viewer["login"]),
        repo_id,
        repo.get_local_branch_name(console_env, git_env),
        prs,
    )


def get_commits(pr_node) -> List[GithubCommit]:
    commits = []
    for commit_node_item in pr_node["commits"]["nodes"]:
        commit_node = commit_node_item["commit"]
        title = CommitTitle(commit_node["messageHeadline"])
        body = CommitBody(commit_node["messageBody"])
        token = zen_token.find_in_body(body)
        commits.append(
            GithubCommit(
                zen_token=token,
                hash=CommitHash(commit_node["oid"]),
                headline=title,
                body=body,
                wip=CommitWipStatus(title.value.startswith("WIP ")),
            )
        )
    return commits


def add_comment(
    console_env: console.Env,
    github_env: Env,
    pull_request: PullRequest,
    comment: str,
) -> None:
    github_env._gh(
        console_env,
        f"pr comment {pull_request.number.value} --body '{comment}'",
    )


def close_pull_request(
    console_env: console.Env,
    github_env: Env,
    pull_request: PullRequest,
) -> None:
    github_env._gh(console_env, f"pr close {pull_request.number.value}")


def close_pull_request_with_comment(
    console_env: console.Env,
    github_env: Env,
    pull_request: PullRequest,
    comment: str,
) -> None:
    github_env._gh(
        console_env,
        f"pr close {pull_request.number.value} --comment '{comment}'",
    )


def create_pull_request(
    console_env: console.Env,
    github_env: Env,
    head: GitBranchName,
    base: GitBranchName,
    commit: GitCommit,
) -> None:
    github_env._gh(
        console_env,
        "pr create "
        f"--head {head.value} "
        f"--base {base.value} "
        f"--title '{commit.messageHeadline.value}' "
        f"--body '{commit.messageBody.value}'",
    )


def update_pull_request(
    console_env: console.Env,
    github_env: Env,
    pr_branch: GitBranchName,
    base: GitBranchName,
    commit: GitCommit,
) -> None:
    github_env._gh(
        console_env,
        f"pr edit {pr_branch.value} "
        f"--base {base.value} "
        f"--title '{commit.messageHeadline.value}' "
        f"--body '{commit.messageBody.value}'",
    )
