from os.path import exists
from typing import List

import yaml

from gitzen import envs
from gitzen.console import say
from gitzen.types import GitBranchName, GitRemoteName, GitRootDir


class Config:
    _root_dir: GitRootDir
    _default_remote_branch: GitBranchName
    _remote_branches: List[GitBranchName]
    _remote: GitRemoteName

    def __init__(
        self,
        root_dir: GitRootDir,
        default_remote_branch: GitBranchName,
        remote_branches: List[GitBranchName],
        remote: GitRemoteName,
    ) -> None:
        self._root_dir = root_dir
        self._default_remote_branch = default_remote_branch
        self._remote_branches = remote_branches
        self._remote = remote

    @property
    def root_dir(self) -> GitRootDir:
        return self._root_dir

    @property
    def default_remote_branch(self) -> GitBranchName:
        return self._default_remote_branch

    @property
    def remote_branches(self) -> List[GitBranchName]:
        return self._remote_branches

    @property
    def remote(self) -> GitRemoteName:
        return self._remote

    def __eq__(self, __o: object) -> bool:
        return (
            self.root_dir == __o.root_dir
            and self.default_remote_branch == __o.default_remote_branch
            and self.remote_branches == __o.remote_branches
            and self.remote == __o.remote
        )


def default_config(root_dir: GitRootDir) -> Config:
    return Config(
        root_dir,
        default_remote_branch=GitBranchName("master"),
        remote_branches=[],
        remote=GitRemoteName("origin"),
    )


def load(
    console_env: envs.ConsoleEnv,
    root_dir: GitRootDir,
) -> Config:
    config_file = f"{root_dir.value}/.gitzen.yml"
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
    return default_config(root_dir)


def read_yaml(file_name):
    with open(file_name, "r") as f:
        return yaml.load(f.read(), Loader=yaml.FullLoader)
