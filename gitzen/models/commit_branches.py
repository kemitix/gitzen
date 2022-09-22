from typing import Optional

from gitzen.models.git_commit import GitCommit
from gitzen.models.github_pull_request import PullRequest
from gitzen.types import GitBranchName


class CommitBranches:
    _git_commit: GitCommit
    _base: GitBranchName
    _head: GitBranchName
    _pull_request: Optional[PullRequest]
    _remote_target: Optional[GitBranchName]

    def __init__(
        self,
        commit: GitCommit,
        base: GitBranchName,
        head: GitBranchName,
        pull_request: Optional[PullRequest] = None,
        remote_target: Optional[GitBranchName] = None,
    ) -> None:
        self._git_commit = commit
        self._base = base
        self._head = head
        self._pull_request = pull_request
        self._remote_target = remote_target

    def __eq__(self, __o: object) -> bool:
        return (
            isinstance(__o, CommitBranches)
            and self._git_commit == __o._git_commit
            and self._base == __o._base
            and self._head == __o.head
            and self._pull_request == __o._pull_request
            and self._remote_target == __o._remote_target
        )

    def __repr__(self) -> str:
        return (
            "CommitBranches("
            f"git_commit={self.git_commit}, \n"
            f"base={self.base}, \n"
            f"head={self.head}, \n"
            f"pull_request={self.pull_request}, \n"
            f"remote_target={self.remote_target}"
            ")"
        )

    @property
    def git_commit(self) -> GitCommit:
        return self._git_commit

    @property
    def base(self) -> GitBranchName:
        return self._base

    @property
    def head(self) -> GitBranchName:
        return self._head

    @property
    def pull_request(self) -> Optional[PullRequest]:
        return self._pull_request

    @property
    def remote_target(self) -> Optional[GitBranchName]:
        return self._remote_target
