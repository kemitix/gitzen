from gitzen.branches import get_remote_branch
from gitzen.config import Config


def test_get_remote_branch_name_returns_default_when_no_match():
    """
    Tests that getRemoteBranchName returns the default remote branch from
    config if it fails to match the local branch name in the list of mapped
    remote branches as listed in the repo's config.
    """
    # given
    defaultBranch = "foo"
    config = Config(
        default_remote_branch=defaultBranch,
        remote_branches=["baz"],
        remote="origin",
    )
    # when
    result = get_remote_branch("other", config)
    # then
    assert result == defaultBranch


def test_get_remote_branch_name_returns_default_when_second_remote_matches():
    """
    Tests that getRemoteBranchName returns the default remote branch from
    config if it fails to match the local branch name in the list of mapped
    remote branches as listed in the repo's config.
    """
    # given
    defaultBranch = "foo"
    config = Config(
        default_remote_branch=defaultBranch,
        remote_branches=["baz", "other"],
        remote="origin",
    )
    # when
    result = get_remote_branch("other", config)
    # then
    assert result == "other"
