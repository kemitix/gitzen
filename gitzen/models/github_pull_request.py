from typing import List

from gitzen.models.github_commit import Commit


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
