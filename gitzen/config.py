from os.path import exists
from typing import List

import bios


class Config:
    defaultRemoteBranch: str
    remoteBranchNames: List[str]
    remote: str

    def __init__(
        self,
        defaultRemoteBranch: str,
        remoteBranches: str,
        remote: str,
    ):
        self.defaultRemoteBranch = defaultRemoteBranch
        self.remoteBranchNames = remoteBranches
        self.remote = remote

    def __eq__(self, __o: object) -> bool:
        return (
            self.defaultRemoteBranch == __o.defaultRemoteBranch
            and self.remoteBranchNames == __o.remoteBranchNames
            and self.remote == __o.remote
        )

    def __repr__(self) -> str:
        return (
            "Config("
            f"defaultRemoteBranch={repr(self.defaultRemoteBranch)}, "
            f"remoteBranchNames={repr(self.remoteBranchNames)}, "
            f"remote={self.remote}, "
            ")"
        )


defaultConfig: Config = Config(
    defaultRemoteBranch="master", remoteBranches=[], remote="origin"
)


def load(dir: str) -> Config:
    configFile = f"{dir}/.gitzen.yml"
    if exists(configFile):
        print(f"Reading config from {configFile}")
        gitzenYml = bios.read(configFile)
        return Config(
            defaultRemoteBranch=gitzenYml["defaultRemoteBranch"],
            remoteBranches=gitzenYml["remoteBranches"],
            remote=gitzenYml["remote"],
        )
    print(f"Using default config - no file: {configFile}")
    return defaultConfig
