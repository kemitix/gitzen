import shlex
from pathlib import PosixPath
from subprocess import DEVNULL, run
from typing import List

from gitzen import config, console
from gitzen.types import GitBranchName


def test_load_when_file_not_found(tmp_path) -> None:
    # given
    # a repo with no config file
    given_repo(tmp_path)
    console_env = console.RealConsoleEnv()
    # when
    result = config.load(console_env, tmp_path)
    # then
    assert result == config.default_config


def test_load_when_file_is_found(tmp_path: PosixPath) -> None:
    # given
    # a repo with a config file
    given_repo(tmp_path)
    configFile = f"{tmp_path}/.gitzen.yml"
    given_file(
        configFile,
        [
            "defaultRemoteBranch: drb",
            'remoteBranches: ["rbn"]',
            "remote: other",
        ],
    )
    console_env = console.RealConsoleEnv()
    # when
    result = config.load(console_env, f"{tmp_path}")
    # then
    assert result == config.Config(
        default_remote_branch=GitBranchName("drb"),
        remote_branches=[GitBranchName("rbn")],
        remote="other",
    )


def test_load_aborts_when_file_is_invalid() -> None:
    pass


def given_repo(dir: PosixPath) -> None:
    cmd = shlex.split("git init")
    run(cmd, cwd=dir, stdout=DEVNULL, stderr=DEVNULL)


def given_file(file: str, lines: List[str]) -> None:
    with open(file, "w") as fp:
        contents = "\n".join(lines)
        fp.write(contents)
