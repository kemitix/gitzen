from gitzen.branches import getRemoteBranch
from gitzen.config import Config


def test_getRemoteBranchName_returns_default_when_no_match():
    """
    Tests that getRemoteBranchName returns the default remote branch from
    config if it fails to match the local branch name in the list of mapped
    remote branches as listed in the repo's config.
    """
    # given
    defaultBranch = "foo"
    config = Config(
        defaultRemoteBranch=defaultBranch,
        remoteBranches=["baz"],
        remote="origin",
    )
    # when
    result = getRemoteBranch("other", config)
    # then
    assert result == defaultBranch
