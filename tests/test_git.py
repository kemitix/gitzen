from unittest import mock

from gitzen.git import Git

@mock.patch('subprocess.run')
def test_fetch(mock_subproc_run):
    """
    Test that the correct command is invoked
    """
    #when
    Git.fetch()
    #then
    mock_subproc_run.assert_called_with(['git', 'fetch'])

@mock.patch('subprocess.run')
def test_branch(mock_subproc_run):
    """
    Test that the correct command is invoked
    """
    #when
    Git.branch()
    #then
    mock_subproc_run.assert_called_with(['git', 'branch', '--no-color'])
