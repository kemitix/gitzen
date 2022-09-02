import subprocess
from subprocess import PIPE, CompletedProcess
from typing import List
from unittest import mock

from gitzen import git, repo


@mock.patch("subprocess.run")
def test_rootDir(mock_subproc_run):
    """
    Test that the correct command is invoked
    """
    # when
    repo.root_dir(git.RealGitEnv())
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
    result = repo.root_dir(git.RealGitEnv())
    # then
    assert result == "test-root-dir"


@mock.patch("subprocess.run")
def test_getLocalBranchName_calls_git_branch(mock_subproc_run):
    """
    Test that the correct command is invoked
    """
    # when
    repo.get_local_branch_name(git.RealGitEnv())
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
    result = repo.get_local_branch_name(git.RealGitEnv())
    # then
    assert result == "me"


def test_getRepoDetailsFromRemoteV():
    class TestCase:
        remote: str
        host: str
        owner: str
        name: str
        match: bool

        def __init__(
            self,
            remote: str,
            host: str,
            owner: str,
            name: str,
            match: bool,
        ):
            self.remote = remote
            self.host = host
            self.owner = owner
            self.name = name
            self.match = match

    testCases: List[TestCase] = [
        TestCase(
            "origin  https://github.com/r2/d2.git (push)",
            "github.com",
            "r2",
            "d2",
            True,
        ),
        TestCase(
            "origin  https://github.com/r2/d2.git (fetch)",
            "",
            "",
            "",
            False,
        ),
        TestCase(
            "origin  https://github.com/r2/d2 (push)",
            "github.com",
            "r2",
            "d2",
            True,
        ),
        TestCase(
            "origin  ssh://git@github.com/r2/d2.git (push)",
            "github.com",
            "r2",
            "d2",
            True,
        ),
        TestCase(
            "origin  ssh://git@github.com/r2/d2.git (fetch)",
            "",
            "",
            "",
            False,
        ),
        TestCase(
            "origin  ssh://git@github.com/r2/d2 (push)",
            "github.com",
            "r2",
            "d2",
            True,
        ),
        TestCase(
            "origin  git@github.com:r2/d2.git (push)",
            "github.com",
            "r2",
            "d2",
            True,
        ),
        TestCase(
            "origin  git@github.com:r2/d2.git (fetch)",
            "",
            "",
            "",
            False,
        ),
        TestCase(
            "origin  git@github.com:r2/d2 (push)",
            "github.com",
            "r2",
            "d2",
            True,
        ),
        TestCase(
            "origin  git@gh.enterprise.com:r2/d2.git (push)",
            "gh.enterprise.com",
            "r2",
            "d2",
            True,
        ),
        TestCase(
            "origin  git@gh.enterprise.com:r2/d2.git (fetch)",
            "",
            "",
            "",
            False,
        ),
        TestCase(
            "origin  git@gh.enterprise.com:r2/d2 (push)",
            "gh.enterprise.com",
            "r2",
            "d2",
            True,
        ),
        TestCase(
            "origin  https://github.com/r2/d2-a.git (push)",
            "github.com",
            "r2",
            "d2-a",
            True,
        ),
        TestCase(
            "origin  https://github.com/r2/d2_a.git (push)",
            "github.com",
            "r2",
            "d2_a",
            True,
        ),
    ]
    for testCase in testCases:
        details = repo.get_repo_details_from_remote(testCase.remote)
        host, owner, name, match = details
        assert (
            host == testCase.host
        ), f"host match failed for {testCase.remote}, got '{host}'"
        assert (
            owner == testCase.owner
        ), f"owner match failed for {testCase.remote}, got '{owner}'"
        assert (
            name == testCase.name
        ), f"name match failed for {testCase.remote}, got '{name}'"
        assert (
            match == testCase.match
        ), f"match match failed for {testCase.remote}, got '{match}'"
