import json
import re
import shlex
import subprocess
from typing import Any, Dict, List

import jmespath

from gitzen import envs, repo
from gitzen.models.github_commit import Commit
from gitzen.models.github_info import GithubInfo
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
queryStatus = """query($repo_owner: String!, $repo_name: String!){
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


def fetchInfo(gitGithubEnv: envs.GitGithubEnv) -> GithubInfo:
    data = gitGithubEnv.githubEnv.graphql(
        {
            "repo_owner": "{owner}",
            "repo_name": "{repo}",
        },
        queryStatus,
        "data",
    )
    repo_id = data["repository"]["id"]
    viewer = data["viewer"]
    prNodes = viewer["repository"]["pullRequests"]["nodes"]
    prs: List[PullRequest] = []
    print(f"Found {len(prNodes)} prs")
    for prNode in prNodes:
        pr_repo_id = prNode["repository"]["id"]
        if repo_id != pr_repo_id:
            continue
        base_ref = prNode["baseRefName"]
        head_ref = prNode["headRefName"]
        print(f"{base_ref} <- {head_ref}")
        match = re.search(r"^gitzen/pr/(?P<localBranch>.*)$", head_ref)
        if match is None:
            continue
        if match.group("localBranch") != base_ref:
            print("ignore prs that don't target expected base branch ???")
            continue
        reviewNode = prNode["reviewDecision"]
        reviewDecision = reviewNode if reviewNode is not None else ""
        prs.append(
            PullRequest(
                id=prNode["id"],
                number=prNode["number"],
                title=prNode["title"],
                baseRefName=base_ref,
                headRefName=head_ref,
                mergeable=prNode["mergeable"],
                reviewDecision=reviewDecision,
                repoId=pr_repo_id,
                commits=getCommits(prNode),
            )
        )
    print(f"Kept {len(prs)} prs")
    return GithubInfo(
        username=viewer["login"],
        repo_id=repo_id,
        local_branch=repo.getLocalBranchName(gitGithubEnv.gitEnv),
        pull_requests=prs,
    )


def getCommits(prNode):
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
    return commits
