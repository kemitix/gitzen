from os.path import exists
from typing import List

import bios


class GitZenConfig:
    defaultRemoteBranch: str
    remoteBranchNames: List[str]

    def __init__(self, defaultRemoteBranch: str, remoteBranches: str) -> None:
        self.defaultRemoteBranch = defaultRemoteBranch
        self.remoteBranchNames = remoteBranches

    def __eq__(self, __o: object) -> bool:
        return (
            self.defaultRemoteBranch == __o.defaultRemoteBranch
            and self.remoteBranchNames == __o.remoteBranchNames
        )

    def __repr__(self) -> str:
        return (
            "GitZenConfig("
            f"defaultRemoteBranch={repr(self.defaultRemoteBranch)}, "
            f"remoteBranchNames={repr(self.remoteBranchNames)}, "
            ")"
        )


defaultConfig: GitZenConfig = GitZenConfig(
    defaultRemoteBranch="master", remoteBranches=[]
)


def load(dir: str):
    configFile = f"{dir}/.gitzen.yml"
    if exists(configFile):
        print(f"Reading config from {configFile}")
        gitzenYml = bios.read(configFile)
        return GitZenConfig(
            defaultRemoteBranch=gitzenYml["defaultRemoteBranch"],
            remoteBranches=gitzenYml["remoteBranches"],
        )
    print(f"Using default config - no file: {configFile}")
    return defaultConfig
