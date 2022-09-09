import json
import re
import shlex
import subprocess
from typing import Any, Dict, List

from gitzen import envs, repo, zen_token
from gitzen.console import say
from gitzen.models.github_commit import Commit
from gitzen.models.github_info import GithubInfo
from gitzen.models.github_pull_request import PullRequest


class RealGithubEnv(envs.GithubEnv):
    def graphql(
        self,
        params: Dict[str, str],
        query: str,
    ) -> Dict[str, Any]:
        args = shlex.split("gh api graphql")
        for pair in params:
            args.append("-F")
            args.append(f"{pair}=" + params[pair])
        args.append("-f")
        args.append(f"query={query}")
        result: subprocess.CompletedProcess[bytes] = subprocess.run(
            args, stdout=subprocess.PIPE
        )
        stdout = result.stdout
        if stdout:
            return json.loads(stdout.decode())
        else:
            return {}  # TODO return some error condition

    def gh(self, args: str) -> List[str]:
        gh_command = f"gh {args}"
        print(f"> {gh_command}")
        result: subprocess.CompletedProcess[bytes] = subprocess.run(
            shlex.split(gh_command), stdout=subprocess.PIPE
        )
        stdout = result.stdout
        if stdout:
            lines = stdout.decode().splitlines()
            return lines
        else:
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
    console_env: envs.ConsoleEnv,
    gitGithubEnv: envs.GitGithubEnv,
) -> GithubInfo:
    data = gitGithubEnv.github_env.graphql(
        {
            "repo_owner": "{owner}",
            "repo_name": "{repo}",
        },
        query_status,
    )["data"]
    repo_id = data["repository"]["id"]
    viewer = data["viewer"]
    pr_nodes = viewer["repository"]["pullRequests"]["nodes"]
    prs: List[PullRequest] = []
    say(console_env, f"Found {len(pr_nodes)} prs")
    for pr_node in pr_nodes:
        pr_repo_id = pr_node["repository"]["id"]
        if repo_id != pr_repo_id:
            continue
        base_ref = pr_node["baseRefName"]
        head_ref = pr_node["headRefName"]
        say(console_env, f"{base_ref} <- {head_ref}")
        match = re.search(r"^gitzen/pr/(?P<localBranch>.*)$", head_ref)
        if match is None:
            continue
        if match.group("localBranch") != base_ref:
            say(
                console_env,
                "ignore prs that don't target expected base branch ???",
            )
            continue
        review_node = pr_node["reviewDecision"]
        review_decision = review_node if review_node is not None else ""
        body = pr_node["body"]
        token = zen_token.find_in_body(body)
        if token is None:
            continue
        prs.append(
            PullRequest(
                id=pr_node["id"],
                zen_token=token,
                number=f'{pr_node["number"]}',
                title=pr_node["title"],
                body=body,
                baseRefName=base_ref,
                headRefName=head_ref,
                mergeable=pr_node["mergeable"],
                reviewDecision=review_decision,
                repoId=pr_repo_id,
                commits=get_commits(pr_node),
            )
        )
    say(console_env, f"Kept {len(prs)} prs")
    return GithubInfo(
        username=viewer["login"],
        repo_id=repo_id,
        local_branch=repo.get_local_branch_name(gitGithubEnv.git_env),
        pull_requests=prs,
    )


def get_commits(pr_node) -> List[Commit]:
    commits = []
    for commit_node_item in pr_node["commits"]["nodes"]:
        commit_node = commit_node_item["commit"]
        title = commit_node["messageHeadline"]
        body = commit_node["messageBody"]
        token = zen_token.find_in_body(body)
        commits.append(
            Commit(
                zen_token=token,
                hash=commit_node["oid"],
                headline=title,
                body=body,
                wip=title.startswith("WIP "),
            )
        )
    return commits


def add_comment(
    github_env: envs.GithubEnv,
    pull_request: PullRequest,
    comment: str,
) -> None:
    github_env.gh(f"pr comment {pull_request.number} --body '{comment}'")


def close_pull_request(
    github_env: envs.GithubEnv,
    pull_request: PullRequest,
) -> None:
    github_env.gh(f"pr close {pull_request.number}")


def close_pull_request_with_comment(
    github_env: envs.GithubEnv,
    pull_request: PullRequest,
    comment: str,
) -> None:
    github_env.gh(f"pr close {pull_request.number} --comment '{comment}'")
