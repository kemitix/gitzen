from os.path import exists
from typing import List

import yaml

from gitzen import envs
from gitzen.console import say
from gitzen.types import GitBranchName, GitRemoteName


class Config:
    root_dir: str
    default_remote_branch: GitBranchName
    remote_branches: List[GitBranchName]
    remote: GitRemoteName

    def __init__(
        self,
        root_dir: str,
        default_remote_branch: GitBranchName,
        remote_branches: List[GitBranchName],
        remote: GitRemoteName,
    ) -> None:
        self.root_dir = root_dir
        self.default_remote_branch = default_remote_branch
        self.remote_branches = remote_branches
        self.remote = remote

    def __eq__(self, __o: object) -> bool:
        return (
            self.root_dir == __o.root_dir
            and self.default_remote_branch == __o.default_remote_branch
            and self.remote_branches == __o.remote_branches
            and self.remote == __o.remote
        )

    @property
    def gitzen_refs(self) -> str:
        return f"{self.root_dir}/.git/refs/gitzen"

    @property
    def gitzen_patches(self) -> str:
        return f"{self.root_dir}/.git/refs/gitzen/patches"


def default_config(root_dir: str) -> Config:
    return Config(
        root_dir,
        default_remote_branch=GitBranchName("master"),
        remote_branches=[],
        remote=GitRemoteName("origin"),
    )


def load(
    console_env: envs.ConsoleEnv,
    root_dir: str,
) -> Config:
    config_file = f"{root_dir}/.gitzen.yml"
    if exists(config_file):
        say(console_env, f"Reading config from {config_file}")
        gitzen_yml = read_yaml(config_file)
        default_branch = GitBranchName(gitzen_yml["defaultRemoteBranch"])
        remote_branches = [
            GitBranchName(branch) for branch in gitzen_yml["remoteBranches"]
        ]
        return Config(
            root_dir,
            default_branch,
            remote_branches,
            GitRemoteName(gitzen_yml["remote"]),
        )
    say(console_env, f"Using default config - no file: {config_file}")
    return default_config(root_dir)


def read_yaml(file_name):
    with open(file_name, "r") as f:
        return yaml.load(f.read(), Loader=yaml.FullLoader)
