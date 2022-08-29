import json
import shlex
import subprocess
from typing import Any, Dict, List

from jmespath import search as jq


class Env:
    def graphql(
        self,
        params: Dict[str, str],
        query,
        path: str,
    ) -> Dict[str, Any]:
        pass


class RealEnv:
    def graphql(
        self,
        params: Dict[str, str],
        query,
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
            return jq(path, json.loads(stdout.decode()))
        else:
            return {}  # TODO return some error condition


class Commit:
    oid: str
    messageHeadline: str
    messageBody: str
    status: str  # enum

    def __init__(self, oid: str, headline: str, body: str, status: str):
        self.oid = oid
        self.messageHeadline = headline
        self.messageBody = body
        self.status = status

    def __eq__(self, __o: object) -> bool:
        return (
            self.oid == __o.oid
            and self.messageHeadline == __o.messageHeadline
            and self.messageBody == __o.messageBody
            and self.status == __o.status
        )

    def __repr__(self) -> str:
        return (
            f"Commit(oid={repr(self.oid)}, "
            f"messageHeadline={repr(self.messageHeadline)}, "
            f"messageBody={repr(self.messageBody)}, "
            f"status={repr(self.status)})"
        )


class PullRequest:
    id: str
    number: int
    title: str
    baseRefName: str
    headRefName: str
    mergeable: str  # enum
    reviewDecision: str  # enum
    repoId: str
    commits: List[Commit]

    def __init__(
        self,
        id: str,
        number: str,
        title: str,
        baseRefName: str,
        headRefName: str,
        mergeable: str,
        reviewDecision: str,
        repoId: str,
        commits: List[Commit],
    ):
        self.id = id
        self.number = number
        self.title = title
        self.baseRefName = baseRefName
        self.headRefName = headRefName
        self.mergeable = mergeable
        self.reviewDecision = reviewDecision
        self.repoId = repoId
        self.commits = commits

    def __eq__(self, __o: object) -> bool:
        return (
            self.id == __o.id
            and self.number == __o.number
            and self.title == __o.title
            and self.baseRefName == __o.baseRefName
            and self.headRefName == __o.headRefName
            and self.mergeable == __o.mergeable
            and self.reviewDecision == __o.reviewDecision
            and self.repoId == __o.repoId
            and self.commits == __o.commits
        )

    def __repr__(self) -> str:
        return (
            "PullRequest("
            f"id={repr(self.id)}, "
            f"number={repr(self.number)}, "
            f"title={repr(self.title)}, "
            f"baseRefName={repr(self.baseRefName)}, "
            f"headRefName={repr(self.baseRefName)}, "
            f"mergeable={repr(self.mergeable)}, "
            f"reviewDecision={repr(self.reviewDecision)}, "
            f"repoId={repr(self.repoId)}, "
            f"commit={repr(self.commits)})"
        )


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


def pullRequests(env: Env) -> List[PullRequest]:
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
            commit = Commit(
                oid=commitNode["oid"],
                headline=commitNode["messageHeadline"],
                body=commitNode["messageBody"],
                status=commitNode["statusCheckRollup"]["state"],
            )
            commits.append(commit)
        reviewNode = prNode["reviewDecision"]
        reviewDecision = reviewNode if reviewNode is not None else ""
        pr = PullRequest(
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
        prs.append(pr)
    return prs
