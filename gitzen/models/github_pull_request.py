from typing import List

from gitzen.models.github_commit import Commit
from gitzen.types import (
    GithubRepoId,
    GitRefName,
    PullRequestBody,
    PullRequestId,
    PullRequestNumber,
    PullRequestTitle,
    ZenToken,
)


class PullRequest:
    id: PullRequestId
    zen_token: ZenToken
    number: PullRequestNumber
    title: PullRequestTitle
    body: PullRequestBody
    baseRefName: GitRefName
    headRefName: GitRefName
    mergeable: str  # enum
    reviewDecision: str  # enum
    repoId: GithubRepoId
    commits: List[Commit]

    def __init__(
        self,
        id: PullRequestId,
        zen_token: ZenToken,
        number: PullRequestNumber,
        title: PullRequestTitle,
        body: PullRequestBody,
        baseRefName: GitRefName,
        headRefName: GitRefName,
        mergeable: str,
        reviewDecision: str,
        repoId: GithubRepoId,
        commits: List[Commit],
    ) -> None:
        self.id = id
        self.zen_token = zen_token
        self.number = number
        self.title = title
        self.body = body
        self.baseRefName = baseRefName
        self.headRefName = headRefName
        self.mergeable = mergeable
        self.reviewDecision = reviewDecision
        self.repoId = repoId
        self.commits = commits

    def __eq__(self, __o: object) -> bool:
        return (
            isinstance(__o, PullRequest)
            and self.id == __o.id
            and self.zen_token == __o.zen_token
            and self.number == __o.number
            and self.title == __o.title
            and self.body == __o.body
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
            f"id={self.id}, "
            f"zen_token={self.zen_token}, "
            f"number={self.number}, "
            f"title={self.title}, "
            f"body={self.body}, "
            f"baseRefName={self.baseRefName}, "
            f"headRefName={self.baseRefName}, "
            f"mergeable={self.mergeable}, "
            f"reviewDecision={self.reviewDecision}, "
            f"repoId={self.repoId}, "
            f"commit={repr(self.commits)})"
        )
