from pathlib import PosixPath

from gitzen import config, console, git
from gitzen.types import GitBranchName, GitRemoteName

from .fakes.repo_files import given_file, given_repo


def test_load_when_file_not_found(tmp_path: PosixPath) -> None:
    # given
    # a repo with no config file
    git_env = git.RealGitEnv()
    root_dir = given_repo(git_env, tmp_path)
    console_env = console.RealConsoleEnv()
    # when
    result = config.load(console_env, root_dir)
    # then
    assert result == config.default_config(root_dir)


def test_load_when_file_is_found(tmp_path: PosixPath) -> None:
    # given
    # a repo with a config file
    git_env = git.RealGitEnv()
    root_dir = given_repo(git_env, tmp_path)
    configFile = f"{root_dir.value}/.gitzen.yml"
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
    result = config.load(console_env, root_dir)
    # then
    assert result == config.Config(
        root_dir,
        GitBranchName("drb"),
        [GitBranchName("rbn")],
        GitRemoteName("other"),
    )


def test_load_aborts_when_file_is_invalid() -> None:
    # TODO
    pass
