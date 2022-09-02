import shlex
from pathlib import PosixPath
from subprocess import DEVNULL, run
from typing import List

from gitzen import config


def test_load_returns_default_config_when_file_not_found(tmp_path):
    # given
    # a repo with no config file
    given_repo(tmp_path)
    # when
    result = config.load(tmp_path)
    # then
    assert result == config.default_config


def test_load_returns_parsed_config_when_file_is_found(tmp_path: PosixPath):
    # given
    # a repo with a config file
    given_repo(tmp_path)
    configFile = f"{tmp_path}/.gitzen.yml"
    givenFile(
        configFile,
        [
            "defaultRemoteBranch: drb",
            'remoteBranches: ["rbn"]',
            "remote: other",
        ],
    )
    # when
    result = config.load(tmp_path)
    # then
    assert result == config.Config(
        default_remote_branch="drb", remote_branches=["rbn"], remote="other"
    )


def test_load_aborts_when_file_is_invalid():
    pass


def given_repo(dir: PosixPath):
    cmd = shlex.split("git init")
    run(cmd, cwd=dir, stdout=DEVNULL, stderr=DEVNULL)


def givenFile(file: PosixPath, lines: List[str]):
    with open(file, "w") as fp:
        contents = "\n".join(lines)
        fp.write(contents)
