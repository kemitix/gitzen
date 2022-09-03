import pytest
from faker import Faker

from gitzen import branches, config, exit_code


def test_get_remote_branch_name_returns_default_when_no_match():
    """
    Tests that getRemoteBranchName returns the default remote branch from
    config if it fails to match the local branch name in the list of mapped
    remote branches as listed in the repo's config.
    """
    # given
    defaultBranch = "foo"
    cfg = config.Config(
        default_remote_branch=defaultBranch,
        remote_branches=["baz"],
        remote="origin",
    )
    # when
    result = branches.get_remote_branch("other", cfg)
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
    cfg = config.Config(
        default_remote_branch=defaultBranch,
        remote_branches=["baz", "other"],
        remote="origin",
    )
    # when
    result = branches.get_remote_branch("other", cfg)
    # then
    assert result == "other"


def test_validate_not_remote_pr_when_not_remote_pr():
    # when
    branches.validate_not_remote_pr("foo")
    # then
    assert True  # did not exit


def test_validate_not_remote_pr_when_is_remote_pr():
    # when
    with pytest.raises(SystemExit) as system_exit:
        branches.validate_not_remote_pr("gitzen/pr/kemitix/master/efd33424")
    # then
    assert system_exit.type == SystemExit
    assert system_exit.value.code == exit_code.REMOTE_PR_CHECKED_OUT


def test_get_required_remote_branch_when_present_in_default_branch():
    # given
    local_branch = Faker().word()
    cfg = config.Config(
        default_remote_branch=local_branch,
        remote="origin",
        remote_branches=[]
    )
    # when
    result = branches.get_required_remote_branch(local_branch, cfg)
    # then
    assert result == local_branch


def test_get_required_remote_branch_when_present_in_remote_branches():
    # given
    local_branch = Faker().word()
    cfg = config.Config(
        default_remote_branch="master",
        remote="origin",
        remote_branches=[local_branch]
    )
    # when
    result = branches.get_required_remote_branch(local_branch, cfg)
    # then
    assert result == local_branch


def test_get_required_remote_branch_when_not_present():
    # given
    local_branch = Faker().word()
    cfg = config.Config(
        default_remote_branch="",
        remote="origin",
        remote_branches=[]
    )
    # when
    with pytest.raises(SystemExit) as system_exit:
        branches.get_required_remote_branch(local_branch, cfg)
    # then
    assert system_exit.type == SystemExit
    assert system_exit.value.code == exit_code.REMOTE_BRANCH_NOT_FOUND
