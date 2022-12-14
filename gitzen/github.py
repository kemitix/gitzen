import json
import re
import shlex
import subprocess
from typing import Any, Dict, List

# trunk-ignore(flake8/E501)
from gitzen import console, exit_code, git, github, logger, patterns, repo, zen_token
from gitzen.models.git_commit import GitCommit
from gitzen.models.github_commit import GithubCommit
from gitzen.models.github_info import GithubInfo
from gitzen.models.github_pull_request import PullRequest
from gitzen.models.gitzen_error import GitZenError
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
        params: Dict[str, str],
        query: str,
    ) -> Dict[str, Any]:
        pass

    def _gh(
        self,
        args: str,
    ) -> List[str]:
        pass


class RealEnv(github.Env):
    logger_env: logger.Env

    def __init__(self, logger_env: logger.Env) -> None:
        super().__init__()
        self.logger_env = logger_env

    def _log(self, message: str) -> None:
        logger.log(self.logger_env, "github", message)

    def _graphql(
        self,
        params: Dict[str, str],
        query: str,
    ) -> Dict[str, Any]:
        cmd = "gh api graphql"
        args = shlex.split(cmd)
        self._log(f"{cmd} ...")
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

    def _gh(
        self,
        args: str,
    ) -> List[str]:
        self._log(args)
        gh_command = shlex.split(f"gh {args}")
        result = subprocess.run(
            gh_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        stdout = result.stdout
        if stdout:
            lines = stdout.decode().splitlines()
            [self._log(f"| {line}") for line in lines]
            self._log("\\------------------")
            return lines
        else:
            self._log("\\------------------")
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
    console.info(console_env, "Contacting Github for existing Pull Requests")
    data = github_env._graphql(
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
    console.info(console_env, f"Found {len(pr_nodes)} Pull Requests")
    for pr_node in pr_nodes:
        pr_repo_id = GithubRepoId(pr_node["repository"]["id"])
        if repo_id != pr_repo_id:
            continue
        base_ref = GitBranchName(pr_node["baseRefName"])
        head_ref = GitBranchName(pr_node["headRefName"])
        console.info(console_env, f" - {base_ref.value} <- {head_ref.value}")
        match = re.search(patterns.remote_pr_branch, head_ref.value)
        if match is None:
            console.info(
                console_env,
                f"Ignoring Pull Request not created by us: {head_ref.value}",
            )
            continue
        review_node = pr_node["reviewDecision"]
        review_decision = PullRequestReviewDecision(
            review_node if review_node is not None else ""
        )
        body = PullRequestBody(pr_node["body"])
        token = zen_token.find_in_body(body)
        commits = get_commits(pr_node)
        if token is None:
            # look in commits
            for commit in commits:
                token = zen_token.find_in_body(commit.messageBody)
                if token is not None:
                    break
            if token is None:  # after checking all commits
                console.info(
                    console_env,
                    "Ignoring Pull Request that doesn't have a zen-token",
                )
                continue
        headHash = commits[-1].hash
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
                headHash,
                PullRequestMergeable(pr_node["mergeable"]),
                review_decision,
                pr_repo_id,
                commits,
            )
        )
    console.info(console_env, f"Kept {len(prs)} Pull Requests")
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
    github_env: Env,
    pull_request: PullRequest,
    comment: str,
) -> None:
    github_env._gh(
        f"pr comment {pull_request.number.value} --body '{comment}'",
    )


def close_pull_request(
    github_env: Env,
    pull_request: PullRequest,
) -> None:
    github_env._gh(f"pr close {pull_request.number.value}")


def close_pull_request_with_comment(
    github_env: Env,
    pull_request: PullRequest,
    comment: str,
) -> None:
    github_env._gh(
        f"pr close {pull_request.number.value} --comment '{comment}'",
    )


def create_pull_request(
    github_env: Env,
    head: GitBranchName,
    base: GitBranchName,
    commit: GitCommit,
) -> None:
    if zen_token.find_in_body(commit.messageBody):
        body = commit.messageBody
    else:
        raise GitZenError(
            exit_code.ZEN_TOKENS_MISSING,
            (
                "zen-token not found in commit body. "
                "Is the Git Zen pre-commit hook installed? "
                "Run 'git zen init' to install the pre-commit hook, then "
                "run 'git rebase @{upstream} --force-rebase' "
                "to add the zen tokens."
            ),
        )
    github_env._gh(
        "pr create "
        f"--head {head.value} "
        f"--base {base.value} "
        # FIXME: escape title for single quotes
        f"--title '{commit.messageHeadline.value}' "
        # FIXME: escape body for single quotes
        f"--body '{body.value}'",
    )


def update_pull_request(
    github_env: Env,
    pr_branch: GitBranchName,
    base: GitBranchName,
    commit: GitCommit,
) -> None:
    if zen_token.find_in_body(commit.messageBody):
        body = commit.messageBody
    else:
        body = CommitBody(
            f"{commit.messageBody.value}\n\nzen-token:{commit.zen_token.value}"
        )
    github_env._gh(
        f"pr edit {pr_branch.value} "
        f"--base {base.value} "
        # FIXME: escape title for single quotes
        f"--title '{commit.messageHeadline.value}' "
        # FIXME: escape body for single quotes
        f"--body '{body.value}'",
    )


def merge_squash(
    github_env: Env,
    pull_request: PullRequest,
) -> List[str]:
    return github_env._gh(
        (
            f"pr merge {pull_request.number.value} "
            "--squash --auto --delete-branch "
            f"--match-head-commit {pull_request.headHash.value} "
        )
    )
