from gitzen.branches import getRemoteBranchName
from gitzen.config import GitZenConfig


def test_getRemoteBranchName_returns_default_when_no_match():
    """
    Tests that getRemoteBranchName returns the default remote branch from config
    if it fails to match the local branch name in the list of mapped remote 
    branches as listed in the repo's config.
    """
    #given
    defaultBranchName = 'foo'
    remoteBranchNames = ['baz']
    config = GitZenConfig(defaultRemoteBranch=defaultBranchName, remoteBranchNames=remoteBranchNames)
    #when
    result = getRemoteBranchName('other', config)
    #then
    assert result == defaultBranchName
