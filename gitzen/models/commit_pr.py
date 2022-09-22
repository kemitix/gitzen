from typing import Optional

from gitzen.models.git_commit import GitCommit
from gitzen.models.github_pull_request import PullRequest
from gitzen.types import ZenToken


class CommitPr:
    _git_commit: GitCommit
    _pull_request: Optional[PullRequest]
    _previous: Optional[ZenToken]

    def __init__(
        self,
        commit: GitCommit,
        pr: Optional[PullRequest],
        previous: Optional[ZenToken] = None,
    ) -> None:
        self._git_commit = commit
        self._pull_request = pr
        self._previous = previous

    def __eq__(self, __o: object) -> bool:
        return (
            isinstance(__o, CommitPr)
            and self._git_commit == __o._git_commit
            and self._pull_request == __o._pull_request
            and self._previous == __o._previous
        )

    def __repr__(self) -> str:
        return (
            "CommitPr("
            f"git_commit={self.git_commit}, "
            f"pull_request={self.pull_request}, "
            f"previous={self.previous}"
            ")"
        )

    @property
    def git_commit(self) -> GitCommit:
        return self._git_commit

    @property
    def pull_request(self) -> Optional[PullRequest]:
        return self._pull_request

    @property
    def previous(self) -> Optional[ZenToken]:
        return self._previous
