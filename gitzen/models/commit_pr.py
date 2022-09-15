from typing import Optional

from gitzen.models.git_commit import GitCommit
from gitzen.models.github_pull_request import PullRequest


class CommitPr:
    _git_commit: GitCommit
    _pull_request: Optional[PullRequest]

    def __init__(self, commit: GitCommit, pr: Optional[PullRequest]) -> None:
        self._git_commit = commit
        self._pull_request = pr

    def __eq__(self, __o: object) -> bool:
        return (
            isinstance(__o, CommitPr)
            and self._git_commit == __o._git_commit
            and self._pull_request == __o._pull_request
        )

    @property
    def git_commit(self) -> GitCommit:
        return self._git_commit

    @property
    def pull_request(self) -> Optional[PullRequest]:
        return self._pull_request
