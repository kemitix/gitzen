from pathlib import PosixPath

from gitzen import config, console, file, git, logger
from gitzen.types import GitBranchName, GitRemoteName

from .fakes.repo_files import given_file, given_repo


def test_load_when_file_not_found(tmp_path: PosixPath) -> None:
    # given
    # a repo with no config file
    file_env = file.RealEnv(logger.RealEnv())
    git_env = git.RealEnv()
    root_dir = given_repo(file_env, git_env, tmp_path)
    console_env = console.RealEnv()
    # when
    result = config.load(console_env, file_env, root_dir)
    # then
    assert result == config.default_config(root_dir)


def test_load_when_file_is_found(tmp_path: PosixPath) -> None:
    # given
    # a repo with a config file
    file_env = file.RealEnv(logger.RealEnv())
    git_env = git.RealEnv()
    root_dir = given_repo(file_env, git_env, tmp_path)
    configFile = f"{root_dir.value}/.gitzen.yml"
    given_file(
        file_env,
        configFile,
        [
            "defaultRemoteBranch: drb",
            'remoteBranches: ["rbn"]',
            "remote: other",
        ],
    )
    console_env = console.RealEnv()
    # when
    result = config.load(console_env, file_env, root_dir)
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
