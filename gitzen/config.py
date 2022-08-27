from typing import List


class GitZenConfig:
    defaultRemoteBranch: str
    remoteBranchNames: List[str]

    def __init__(self, defaultRemoteBranch: str, remoteBranchNames: str) -> None:
        self.defaultRemoteBranch = defaultRemoteBranch
        self.remoteBranchNames = remoteBranchNames

