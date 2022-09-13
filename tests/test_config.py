from pathlib import PosixPath

from gitzen import config, console
from gitzen.types import GitBranchName, GitRemoteName

from .fakes.repo_files import given_file, given_repo


def test_load_when_file_not_found(tmp_path) -> None:
    # given
    # a repo with no config file
    given_repo(tmp_path)
    console_env = console.RealConsoleEnv()
    # when
    result = config.load(console_env, tmp_path)
    # then
    assert result == config.default_config(tmp_path)


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
        f"{tmp_path}",
        GitBranchName("drb"),
        [GitBranchName("rbn")],
        GitRemoteName("other"),
    )


def test_load_aborts_when_file_is_invalid() -> None:
    # TODO
    pass
