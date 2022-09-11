from os.path import exists
from typing import List

import yaml

from gitzen import envs
from gitzen.console import say
from gitzen.types import GitBranchName, GitRemoteName


class Config:
    default_remote_branch: GitBranchName
    remote_branches: List[GitBranchName]
    remote: GitRemoteName

    def __init__(
        self,
        default_remote_branch: GitBranchName,
        remote_branches: List[GitBranchName],
        remote: GitRemoteName,
    ) -> None:
        self.default_remote_branch = default_remote_branch
        self.remote_branches = remote_branches
        self.remote = remote

    def __eq__(self, __o: object) -> bool:
        return (
            self.default_remote_branch == __o.default_remote_branch
            and self.remote_branches == __o.remote_branches
            and self.remote == __o.remote
        )


default_config = Config(
    default_remote_branch=GitBranchName("master"),
    remote_branches=[],
    remote=GitRemoteName("origin"),
)


def load(
    console_env: envs.ConsoleEnv,
    dir: str,
) -> Config:
    config_file = f"{dir}/.gitzen.yml"
    if exists(config_file):
        say(console_env, f"Reading config from {config_file}")
        gitzen_yml = read_yaml(config_file)
        default_branch = GitBranchName(gitzen_yml["defaultRemoteBranch"])
        remote_branches = [
            GitBranchName(branch) for branch in gitzen_yml["remoteBranches"]
        ]
        return Config(
            default_branch,
            remote_branches,
            GitRemoteName(gitzen_yml["remote"]),
        )
    say(console_env, f"Using default config - no file: {config_file}")
    return default_config


def read_yaml(file_name):
    with open(file_name, "r") as f:
        return yaml.load(f.read(), Loader=yaml.FullLoader)
