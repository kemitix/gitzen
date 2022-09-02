from typing import List

from gitzen.models.github_pull_request import PullRequest


class GithubInfo:
    username: str
    repo_id: str
    local_branch: str
    pull_requests: List[PullRequest]

    def __init__(
        self,
        username: str,
        repo_id: str,
        local_branch: str,
        pull_requests: List[PullRequest],
    ) -> None:
        self.username = username
        self.repo_id = repo_id
        self.local_branch = local_branch
        self.pull_requests = pull_requests

    def __eq__(self, __o: object) -> bool:
        return (
            self.username == __o.username
            and self.repo_id == __o.repo_id
            and self.local_branch == __o.local_branch
            and self.pull_requests == __o.pull_requests
        )

    def __repr__(self) -> str:
        return (
            "GithubInfo("
            f"username={self.username}, "
            f"repo_id={self.repo_id}, "
            f"local_branch={self.local_branch}, "
            f"pull_requests={self.pull_requests})"
        )
