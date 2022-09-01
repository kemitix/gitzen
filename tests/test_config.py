import shlex
from pathlib import PosixPath
from subprocess import DEVNULL, run
from typing import List

from gitzen import config


def test_load_returns_default_config_when_file_not_found(tmp_path):
    # given
    # a repo with no config file
    givenRepo(tmp_path)
    # when
    result = config.load(tmp_path)
    # then
    assert result == config.defaultConfig


def test_load_returns_parsed_config_when_file_is_found(tmp_path: PosixPath):
    # given
    # a repo with a config file
    givenRepo(tmp_path)
    configFile = f"{tmp_path}/.gitzen.yml"
    givenFile(
        configFile,
        [
            "defaultRemoteBranch: drb",
            'remoteBranches: ["rbn"]',
        ],
    )
    # when
    result = config.load(tmp_path)
    # then
    assert result == config.Config(
        defaultRemoteBranch="drb",
        remoteBranches=["rbn"],
    )


def test_load_aborts_when_file_is_invalid():
    pass


def givenRepo(dir: PosixPath):
    cmd = shlex.split("git init")
    run(cmd, cwd=dir, stdout=DEVNULL, stderr=DEVNULL)


def givenFile(file: PosixPath, lines: List[str]):
    with open(file, "w") as fp:
        contents = "\n".join(lines)
        fp.write(contents)
