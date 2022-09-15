from typing import Optional

# trunk-ignore(flake8/E501)
from gitzen.types import CommitBody, CommitHash, CommitTitle, CommitWipStatus, ZenToken

from .git_commit import GitCommit


class GithubCommit:
    zen_token: Optional[ZenToken]
    hash: CommitHash
    messageHeadline: CommitTitle
    messageBody: CommitBody
    wip: CommitWipStatus

    def __init__(
        self,
        zen_token: Optional[ZenToken],
        hash: CommitHash,
        headline: CommitTitle,
        body: CommitBody,
        wip: CommitWipStatus,
    ) -> None:
        self.zen_token = zen_token
        self.hash = hash
        self.messageHeadline = headline
        self.messageBody = body
        self.wip = wip

    def __eq__(self, __o: object) -> bool:
        return (
            (isinstance(__o, GithubCommit) or isinstance(__o, GitCommit))
            and self.zen_token == __o.zen_token
            and self.hash == __o.hash
            and self.messageHeadline == __o.messageHeadline
            and self.messageBody == __o.messageBody
            and self.wip == __o.wip
        )

    def __repr__(self) -> str:
        return (
            f"GithubCommit(zen_token={self.zen_token}, "
            f"hash={self.hash}, "
            f"messageHeadline={self.messageHeadline}, "
            f"messageBody={self.messageBody}, "
            f"wip={repr(self.wip)})"
        )

    def as_git_commit(self) -> Optional[GitCommit]:
        if self.zen_token is not None:
            return GitCommit(
                self.zen_token,
                self.hash,
                self.messageHeadline,
                self.messageBody,
                self.wip,
            )
        return None


def from_git_commit(self, git_commit: GitCommit) -> GithubCommit:
    return GithubCommit(
        git_commit.zen_token,
        git_commit.hash,
        git_commit.messageHeadline,
        git_commit.messageBody,
        git_commit.wip,
    )
