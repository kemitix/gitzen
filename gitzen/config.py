from os.path import exists
from typing import List

from gitzen import console, file
from gitzen.types import GitBranchName, GitRemoteName, GitRootDir
from gitzen.wrappers import yaml


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
    console_env: console.Env,
    file_env: file.Env,
    root_dir: GitRootDir,
) -> Config:
    config_file = f"{root_dir.value}/.gitzen.yml"
    if exists(config_file):
        console.info(console_env, f"Reading config from {config_file}")
        gitzen_yml = yaml.read(file_env, config_file)
        default_branch = GitBranchName(gitzen_yml["defaultBranch"])
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
