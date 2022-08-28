from subprocess import PIPE, CompletedProcess
from unittest import mock

from gitzen import git


@mock.patch("subprocess.run")
def test_revParse(mock_subproc_run):
    """
    Test that the correct command is invoked
    """
    # when
    git.revParse("--verify HEAD")
    # then
    gitRevParse = ["git", "rev-parse", "--verify", "HEAD"]
    mock_subproc_run.assert_called_with(gitRevParse, stdout=PIPE)


@mock.patch("subprocess.run")
def test_revParse_returns_value(mock_subproc_run):
    """
    Test that revParse returns the value
    """
    # given
    mock_subproc_run.return_value = CompletedProcess(
        "", 0, stdout="688881f74786d59ff397ef81efe1c137167f46b2".encode()
    )
    # when
    result = git.revParse()
    # then
    assert result == ["688881f74786d59ff397ef81efe1c137167f46b2"]


@mock.patch("subprocess.run")
def test_fetch(mock_subproc_run):
    """
    Test that the correct command is invoked
    """
    # when
    git.fetch()
    # then
    gitFetch = ["git", "fetch"]
    mock_subproc_run.assert_called_with(gitFetch, stdout=PIPE)


@mock.patch("subprocess.run")
def test_branch(mock_subproc_run):
    """
    Test that the correct command is invoked
    """
    # when
    git.branch()
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
def test_remote(mock_subproc_run):
    """
    Test that the correct command is invoked
    """
    # when
    git.remote()
    # then
    mock_subproc_run.assert_called_with(
        [
            "git",
            "remote",
            "--verbose",
        ],
        stdout=PIPE,
    )
