import json
import shlex
import subprocess
from typing import Any, Dict, List

import jmespath

from gitzen.envs import GithubEnv
from gitzen.models.github_commit import Commit
from gitzen.models.github_pull_request import PullRequest


class RealGithubEnv:
    def graphql(
        self,
        params: Dict[str, str],
        query: str,
        path: str,
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
            return jmespath.search(path, json.loads(stdout.decode()))
        else:
            return {}  # TODO return some error condition


# trunk-ignore(flake8/E501)
# GraphQL originally from https://github.com/ejoffe/spr/blob/9597afc52354db66d4b419f7ee7a9bd7eacdf70f/github/githubclient/gen/genclient/operations.go#L72
queryPullRequests = """query($repo_name: String!){
    viewer {
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
}
"""


def pullRequests(env: GithubEnv) -> List[PullRequest]:
    prNodes = env.graphql(
        {"repo_name": "{repo}"},
        queryPullRequests,
        "data.viewer.repository.pullRequests.nodes",
    )
    prs: List[PullRequest] = []
    for prNode in prNodes:
        commits = []
        for commitNodeItem in prNode["commits"]["nodes"]:
            commitNode = commitNodeItem["commit"]
            commits.append(
                Commit(
                    oid=commitNode["oid"],
                    headline=commitNode["messageHeadline"],
                    body=commitNode["messageBody"],
                    status=commitNode["statusCheckRollup"]["state"],
                )
            )
        reviewNode = prNode["reviewDecision"]
        reviewDecision = reviewNode if reviewNode is not None else ""
        prs.append(
            PullRequest(
                id=prNode["id"],
                number=prNode["number"],
                title=prNode["title"],
                baseRefName=prNode["baseRefName"],
                headRefName=prNode["headRefName"],
                mergeable=prNode["mergeable"],
                reviewDecision=reviewDecision,
                repoId=prNode["repository"]["id"],
                commits=commits,
            )
        )
    return prs
