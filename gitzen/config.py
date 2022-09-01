from os.path import exists
from typing import List

import bios


class Config:
    defaultRemoteBranch: str
    remoteBranchNames: List[str]

    def __init__(self, defaultRemoteBranch: str, remoteBranches: str):
        self.defaultRemoteBranch = defaultRemoteBranch
        self.remoteBranchNames = remoteBranches

    def __eq__(self, __o: object) -> bool:
        return (
            self.defaultRemoteBranch == __o.defaultRemoteBranch
            and self.remoteBranchNames == __o.remoteBranchNames
        )

    def __repr__(self) -> str:
        return (
            "Config("
            f"defaultRemoteBranch={repr(self.defaultRemoteBranch)}, "
            f"remoteBranchNames={repr(self.remoteBranchNames)}, "
            ")"
        )


defaultConfig: Config = Config(defaultRemoteBranch="master", remoteBranches=[])


def load(dir: str) -> Config:
    configFile = f"{dir}/.gitzen.yml"
    if exists(configFile):
        print(f"Reading config from {configFile}")
        gitzenYml = bios.read(configFile)
        return Config(
            defaultRemoteBranch=gitzenYml["defaultRemoteBranch"],
            remoteBranches=gitzenYml["remoteBranches"],
        )
    print(f"Using default config - no file: {configFile}")
    return defaultConfig
