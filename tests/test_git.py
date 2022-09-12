from subprocess import PIPE, CompletedProcess
from unittest import mock

from faker import Faker

from gitzen import git
from gitzen.types import GitBranchName


@mock.patch("subprocess.run")
def test_branch(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # when
    git.branch(git.RealGitEnv())
    # then
    mock_subproc_run.assert_called_with(
        [
            "git",
            "branch",
            "--no-color",
        ],
        stdout=PIPE,
    )


@mock.patch("subprocess.run")
def test_fetch(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # when
    git.fetch(git.RealGitEnv())
    # then
    gitFetch = ["git", "fetch"]
    mock_subproc_run.assert_called_with(gitFetch, stdout=PIPE)


@mock.patch("subprocess.run")
def test_log(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # when
    git.log(git.RealGitEnv(), "master..HEAD")
    # then
    gitFetch = ["git", "log", "--no-color", "master..HEAD"]
    mock_subproc_run.assert_called_with(gitFetch, stdout=PIPE)


@mock.patch("subprocess.run")
def test_remote(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # when
    git.remote(git.RealGitEnv())
    # then
    mock_subproc_run.assert_called_with(
        [
            "git",
            "remote",
            "--verbose",
        ],
        stdout=PIPE,
    )


@mock.patch("subprocess.run")
def test_rebase(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # when
    git.rebase(git.RealGitEnv(), GitBranchName("target/branch"))
    # then
    mock_subproc_run.assert_called_with(
        [
            "git",
            "rebase",
            "target/branch",
            "--autostash",
        ],
        stdout=PIPE,
    )


@mock.patch("subprocess.run")
def test_revParse(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # when
    git.rev_parse(git.RealGitEnv(), "--verify HEAD")
    # then
    mock_subproc_run.assert_called_with(
        ["git", "rev-parse", "--verify", "HEAD"], stdout=PIPE
    )


@mock.patch("subprocess.run")
def test_revParse_returns_value(mock_subproc_run) -> None:
    """
    Test that revParse returns the value
    """
    # given
    mock_subproc_run.return_value = CompletedProcess(
        "", 0, stdout="688881f74786d59ff397ef81efe1c137167f46b2".encode()
    )
    # when
    result = git.rev_parse(git.RealGitEnv())
    # then
    assert result == ["688881f74786d59ff397ef81efe1c137167f46b2"]


@mock.patch("subprocess.run")
def test_switch(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # given
    branch = GitBranchName(Faker().word())
    # when
    git.switch(git.RealGitEnv(), branch)
    # then
    mock_subproc_run.assert_called_with(
        [
            "git",
            "switch",
            branch.value,
        ],
        stdout=PIPE,
    )
