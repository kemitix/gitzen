from typing import Optional

from gitzen.models.git_commit import GitCommit
from gitzen.models.github_pull_request import PullRequest
from gitzen.types import GitBranchName


class CommitPr:
    _git_commit: GitCommit
    _pull_request: Optional[PullRequest]
    _base: Optional[GitBranchName]
    _head: Optional[GitBranchName]

    def __init__(
        self,
        commit: GitCommit,
        pr: Optional[PullRequest],
        base: Optional[GitBranchName] = None,
        head: Optional[GitBranchName] = None,
    ) -> None:
        self._git_commit = commit
        self._pull_request = pr
        self._base = base
        self._head = head

    def __eq__(self, __o: object) -> bool:
        return (
            isinstance(__o, CommitPr)
            and self._git_commit == __o._git_commit
            and self._pull_request == __o._pull_request
            and self._base == __o._base
            and self._head == __o.head
        )

    def __repr__(self) -> str:
        return (
            "CommitPr("
            f"git_commit={self.git_commit}, \n"
            f"pull_request={self.pull_request}, \n"
            f"base={self.base}, \n"
            f"head={self.head}"
            ")"
        )

    @property
    def git_commit(self) -> GitCommit:
        return self._git_commit

    @property
    def pull_request(self) -> Optional[PullRequest]:
        return self._pull_request

    @property
    def base(self) -> Optional[GitBranchName]:
        return self._base

    @property
    def head(self) -> Optional[GitBranchName]:
        return self._head
