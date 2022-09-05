import json
import re
import shlex
import subprocess
from typing import Any, Dict, List, Optional

from gitzen import envs, repo
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


def fetch_info(gitGithubEnv: envs.GitGithubEnv) -> GithubInfo:
    data = gitGithubEnv.githubEnv.graphql(
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
    print(f"Found {len(pr_nodes)} prs")
    for pr_node in pr_nodes:
        pr_repo_id = pr_node["repository"]["id"]
        if repo_id != pr_repo_id:
            continue
        base_ref = pr_node["baseRefName"]
        head_ref = pr_node["headRefName"]
        print(f"{base_ref} <- {head_ref}")
        match = re.search(r"^gitzen/pr/(?P<localBranch>.*)$", head_ref)
        if match is None:
            continue
        if match.group("localBranch") != base_ref:
            print("ignore prs that don't target expected base branch ???")
            continue
        review_node = pr_node["reviewDecision"]
        review_decision = review_node if review_node is not None else ""
        prs.append(
            PullRequest(
                id=pr_node["id"],
                number=pr_node["number"],
                title=pr_node["title"],
                baseRefName=base_ref,
                headRefName=head_ref,
                mergeable=pr_node["mergeable"],
                reviewDecision=review_decision,
                repoId=pr_repo_id,
                commits=get_commits(pr_node),
            )
        )
    print(f"Kept {len(prs)} prs")
    return GithubInfo(
        username=viewer["login"],
        repo_id=repo_id,
        local_branch=repo.get_local_branch_name(gitGithubEnv.gitEnv),
        pull_requests=prs,
    )


def get_commits(pr_node) -> List[Commit]:
    commits = []
    for commit_node_item in pr_node["commits"]["nodes"]:
        commit_node = commit_node_item["commit"]
        title = commit_node["messageHeadline"]
        body = commit_node["messageBody"]
        zentoken = get_zentoken(body)
        commits.append(
            Commit(
                zen_token=zentoken,
                hash=commit_node["oid"],
                headline=title,
                body=body,
                wip=title.startswith("WIP "),
            )
        )
    return commits


def get_zentoken(body: str) -> Optional[str]:
    for line in body.splitlines():
        match = re.search(r"^zen-token:(?P<token>[a-f0-9]{8})$", line)
        if match:
            token = match.group("token")
            return token
    return None
