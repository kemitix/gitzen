import subprocess
from unittest import mock

from gitzen import git


@mock.patch("subprocess.run")
def test_fetch(mock_subproc_run):
    """
    Test that the correct command is invoked
    """
    # when
    git.fetch()
    # then
    gitFetch = ["git", "fetch"]
    pipe = subprocess.PIPE
    mock_subproc_run.assert_called_with(gitFetch, stdout=pipe)


@mock.patch("subprocess.run")
def test_branch(mock_subproc_run):
    """
    Test that the correct command is invoked
    """
    # when
    git.branch()
    # then
    mock_subproc_run.assert_called_with(
        ["git", "branch", "--no-color"], stdout=subprocess.PIPE
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
        ["git", "remote", "--verbose"], stdout=subprocess.PIPE
    )
