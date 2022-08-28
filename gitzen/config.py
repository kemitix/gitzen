from typing import List


class GitZenConfig:
    defaultRemoteBranch: str
    remoteBranchNames: List[str]

    def __init__(self, defaultRemoteBranch: str, remoteBranches: str) -> None:
        self.defaultRemoteBranch = defaultRemoteBranch
        self.remoteBranchNames = remoteBranches
