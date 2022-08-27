from subprocess import CompletedProcess
import subprocess
from unittest import mock

from gitzen import repo

@mock.patch('subprocess.run')
def test_localBranch_calls_git_branch(mock_subproc_run):
    """
    Test that the correct command is invoked
    """
    #when
    repo.localBranch()
    #then
    mock_subproc_run.assert_called_with(['git', 'branch', '--no-color'], stdout=subprocess.PIPE)

@mock.patch('subprocess.run')
def test_localBranch_returns_correct_branch(mock_subproc_run):
    """
    Test the localBranch parses the correct branch from the git branch output
    """
    #given
    mock_subproc_run.return_value = CompletedProcess("", 0, 
        stdout="\n".join([
            "  not-me",
            "* me",
            "  not-me-2"
        ]).encode())
    #when
    result = repo.localBranch()
    #then
    assert result == "me"
