from typing import List

from gitzen import config
from gitzen.models.git_commit import GitCommit
from gitzen.models.github_commit import GithubCommit
from gitzen.types import (
    CommitHash,
    GitBranchName,
    GithubRepoId,
    GithubUsername,
    PullRequestBody,
    PullRequestId,
    PullRequestMergeable,
    PullRequestNumber,
    PullRequestReviewDecision,
    PullRequestTitle,
    ZenToken,
)


class PullRequest:
    id: PullRequestId
    zen_token: ZenToken
    number: PullRequestNumber
    author: GithubUsername
    title: PullRequestTitle
    body: PullRequestBody
    baseRefName: GitBranchName
    headRefName: GitBranchName
    headHash: CommitHash
    mergeable: PullRequestMergeable
    reviewDecision: PullRequestReviewDecision
    repoId: GithubRepoId
    commits: List[GithubCommit]

    def __init__(
        self,
        id: PullRequestId,
        zen_token: ZenToken,
        number: PullRequestNumber,
        author: GithubUsername,
        title: PullRequestTitle,
        body: PullRequestBody,
        baseRefName: GitBranchName,
        headRefName: GitBranchName,
        headHash: CommitHash,
        mergeable: PullRequestMergeable,
        reviewDecision: PullRequestReviewDecision,
        repoId: GithubRepoId,
        commits: List[GithubCommit],
    ) -> None:
        self.id = id
        self.zen_token = zen_token
        self.number = number
        self.author = author
        self.title = title
        self.body = body
        self.baseRefName = baseRefName
        self.headRefName = headRefName
        self.headHash = headHash
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
            and self.author == __o.author
            and self.title == __o.title
            and self.body == __o.body
            and self.baseRefName == __o.baseRefName
            and self.headRefName == __o.headRefName
            and self.headHash == __o.headHash
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
            f"author={self.author}, "
            f"title={self.title}, "
            f"body={self.body}, "
            f"baseRefName={self.baseRefName}, "
            f"headRefName={self.baseRefName}, "
            f"headHash={self.headHash}, "
            f"mergeable={self.mergeable}, "
            f"reviewDecision={self.reviewDecision}, "
            f"repoId={self.repoId}, "
            f"commit={repr(self.commits)})"
        )

    @staticmethod
    def create_template(
        commit: GitCommit,
        author: GithubUsername,
        cfg: config.Config,
        branch: GitBranchName,
    ) -> "PullRequest":
        return PullRequest(
            PullRequestId(""),
            commit.zen_token,
            PullRequestNumber(""),
            author,
            PullRequestTitle(commit.messageHeadline.value),
            PullRequestBody(commit.messageBody.value),
            cfg.default_branch,
            branch,
            commit.hash,
            PullRequestMergeable(""),
            PullRequestReviewDecision(""),
            GithubRepoId(""),
            commits=[GithubCommit.from_git_commit(commit)],
        )

    @property
    def short_head_hash(self) -> str:
        return self.headHash.value[:7]
