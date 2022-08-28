import subprocess
from subprocess import PIPE, CompletedProcess
from unittest import mock

from gitzen import repo


@mock.patch("subprocess.run")
def test_rootDir(mock_subproc_run):
    """
    Test that the correct command is invoked
    """
    # when
    repo.rootDir()
    # then
    gitRevParse = ["git", "rev-parse", "--show-toplevel"]
    mock_subproc_run.assert_called_with(gitRevParse, stdout=PIPE)


@mock.patch("subprocess.run")
def test_rootDir_returns_path(mock_subproc_run):
    """
    Test that rootDir returns the directory
    """
    # given
    mock_subproc_run.return_value = CompletedProcess(
        "", 0, stdout="test-root-dir".encode()
    )
    # when
    result = repo.rootDir()
    # then
    assert result == "test-root-dir"


@mock.patch("subprocess.run")
def test_getLocalBranchName_calls_git_branch(mock_subproc_run):
    """
    Test that the correct command is invoked
    """
    # when
    repo.getLocalBranchName()
    # then
    mock_subproc_run.assert_called_with(
        ["git", "branch", "--no-color"], stdout=subprocess.PIPE
    )


@mock.patch("subprocess.run")
def test_getLocalBranchName_returns_correct_branch(mock_subproc_run):
    """
    Test that getLocalBranchName parses the correct branch from the git
    branch output
    """
    # given
    mock_subproc_run.return_value = CompletedProcess(
        "", 0, stdout="\n".join(["  not-me", "* me", "  not-me-2"]).encode()
    )
    # when
    result = repo.getLocalBranchName()
    # then
    assert result == "me"
