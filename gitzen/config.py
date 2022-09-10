from os.path import exists
from typing import List

import yaml

from gitzen import envs
from gitzen.console import say


class Config:
    default_remote_branch: str
    remote_branches: List[str]
    remote: str

    def __init__(
        self,
        default_remote_branch: str,
        remote_branches: List[str],
        remote: str,
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


default_config: Config = Config(
    default_remote_branch="master", remote_branches=[], remote="origin"
)


def load(console_env: envs.ConsoleEnv, dir: str) -> Config:
    config_file = f"{dir}/.gitzen.yml"
    if exists(config_file):
        say(console_env, f"Reading config from {config_file}")
        gitzen_yml = read_yaml(config_file)
        return Config(
            default_remote_branch=gitzen_yml["defaultRemoteBranch"],
            remote_branches=gitzen_yml["remoteBranches"],
            remote=gitzen_yml["remote"],
        )
    say(console_env, f"Using default config - no file: {config_file}")
    return default_config


def read_yaml(file_name):
    f = open(file_name, "r")
    yaml_content = f.read()
    result = yaml.load(yaml_content, Loader=yaml.FullLoader)
    f.close()
    return result
