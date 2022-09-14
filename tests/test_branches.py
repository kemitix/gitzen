import pytest
from faker import Faker

from gitzen import branches, config, console, exit_code
from gitzen.types import GitBranchName, GitRemoteName, GitRootDir


def test_get_remote_branch_name_when_no_match() -> None:
    """
    Tests that getRemoteBranchName returns the default remote branch from
    config if it fails to match the local branch name in the list of mapped
    remote branches as listed in the repo's config.
    """
    # given
    defaultBranch = GitBranchName("foo")
    cfg = config.Config(
        GitRootDir(""),
        default_remote_branch=defaultBranch,
        remote_branches=[GitBranchName("baz")],
        remote=GitRemoteName("origin"),
    )
    # when
    result = branches.get_remote_branch(GitBranchName("other"), cfg)
    # then
    assert result == defaultBranch


def test_get_remote_branch_name_when_second_remote_matches() -> None:
    """
    Tests that getRemoteBranchName returns the default remote branch from
    config if it fails to match the local branch name in the list of mapped
    remote branches as listed in the repo's config.
    """
    # given
    defaultBranch = GitBranchName("foo")
    cfg = config.Config(
        GitRootDir(""),
        default_remote_branch=defaultBranch,
        remote_branches=[GitBranchName("baz"), GitBranchName("other")],
        remote=GitRemoteName("origin"),
    )
    # when
    result = branches.get_remote_branch(GitBranchName("other"), cfg)
    # then
    assert result == GitBranchName("other")


def test_validate_not_remote_pr_when_not_remote_pr() -> None:
    # given
    console_env = console.RealConsoleEnv()
    # when
    branches.validate_not_remote_pr(console_env, GitBranchName("foo"))
    # then
    assert True  # did not exit


def test_validate_not_remote_pr_when_is_remote_pr() -> None:
    # given
    console_env = console.RealConsoleEnv()
    # when
    with pytest.raises(SystemExit) as system_exit:
        branches.validate_not_remote_pr(
            console_env, GitBranchName("gitzen/pr/kemitix/master/efd33424")
        )
    # then
    assert system_exit.type == SystemExit
    assert system_exit.value.code == exit_code.REMOTE_PR_CHECKED_OUT


def test_get_required_remote_branch_when_present_in_default_branch() -> None:
    # given
    local_branch = GitBranchName(Faker().word())
    cfg = config.Config(
        GitRootDir(""),
        default_remote_branch=local_branch,
        remote=GitRemoteName("origin"),
        remote_branches=[],
    )
    console_env = console.RealConsoleEnv()
    # when
    result = branches.get_required_remote_branch(
        console_env,
        local_branch,
        cfg,
    )
    # then
    assert result == local_branch


def test_get_required_remote_branch_when_present_in_remote_branches() -> None:
    # given
    local_branch = GitBranchName(Faker().word())
    cfg = config.Config(
        GitRootDir(""),
        default_remote_branch=GitBranchName("master"),
        remote=GitRemoteName("origin"),
        remote_branches=[local_branch],
    )
    console_env = console.RealConsoleEnv()
    # when
    result = branches.get_required_remote_branch(
        console_env,
        local_branch,
        cfg,
    )
    # then
    assert result == local_branch


def test_get_required_remote_branch_when_not_present() -> None:
    # given
    local_branch = GitBranchName(Faker().word())
    cfg = config.Config(
        GitRootDir(""),
        default_remote_branch=GitBranchName(""),
        remote=GitRemoteName("origin"),
        remote_branches=[],
    )
    console_env = console.RealConsoleEnv()
    # when
    with pytest.raises(SystemExit) as system_exit:
        branches.get_required_remote_branch(console_env, local_branch, cfg)
    # then
    assert system_exit.type == SystemExit
    assert system_exit.value.code == exit_code.REMOTE_BRANCH_NOT_FOUND
