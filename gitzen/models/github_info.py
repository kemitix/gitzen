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
