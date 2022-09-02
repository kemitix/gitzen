from os.path import exists
from typing import List

import bios


class Config:
    default_remote_branch: str
    remote_branch: List[str]
    remote: str

    def __init__(
        self,
        default_remote_branch: str,
        remote_branches: str,
        remote: str,
    ):
        self.default_remote_branch = default_remote_branch
        self.remote_branch = remote_branches
        self.remote = remote

    def __eq__(self, __o: object) -> bool:
        return (
            self.default_remote_branch == __o.default_remote_branch
            and self.remote_branch == __o.remote_branch
            and self.remote == __o.remote
        )

    def __repr__(self) -> str:
        return (
            "Config("
            f"default_remote_branch={repr(self.default_remote_branch)}, "
            f"remote_branch={repr(self.remote_branch)}, "
            f"remote={self.remote}, "
            ")"
        )


default_config: Config = Config(
    default_remote_branch="master", remote_branches=[], remote="origin"
)


def load(dir: str) -> Config:
    config_file = f"{dir}/.gitzen.yml"
    if exists(config_file):
        print(f"Reading config from {config_file}")
        gitzen_yml = bios.read(config_file)
        return Config(
            default_remote_branch=gitzen_yml["defaultRemoteBranch"],
            remote_branches=gitzen_yml["remoteBranches"],
            remote=gitzen_yml["remote"],
        )
    print(f"Using default config - no file: {config_file}")
    return default_config
