import subprocess
from subprocess import PIPE, CompletedProcess
from typing import List
from unittest import mock

from gitzen import console, git, repo
from gitzen.models.github_commit import Commit
from gitzen.types import (
    CommitBody,
    CommitHash,
    CommitTitle,
    CommitWipStatus,
    GitBranchName,
    ZenToken,
)

from .fakes.git_env import FakeGitEnv


@mock.patch("subprocess.run")
def test_rootDir(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # when
    repo.root_dir(git.RealGitEnv())
    # then
    gitRevParse = ["git", "rev-parse", "--show-toplevel"]
    mock_subproc_run.assert_called_with(gitRevParse, stdout=PIPE)


@mock.patch("subprocess.run")
def test_rootDir_returns_path(mock_subproc_run) -> None:
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
def test_getLocalBranchName_calls_git_branch(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # given
    mock_subproc_run.return_value = CompletedProcess(
        "", 0, stdout="* branch-name".encode()
    )
    console_env = console.RealConsoleEnv()
    # when
    repo.get_local_branch_name(console_env, git.RealGitEnv())
    # then
    mock_subproc_run.assert_called_with(
        ["git", "branch", "--no-color"], stdout=subprocess.PIPE
    )


@mock.patch("subprocess.run")
def test_getLocalBranchName_returns_correct_branch(mock_subproc_run) -> None:
    """
    Test that getLocalBranchName parses the correct branch from the git
    branch output
    """
    # given
    mock_subproc_run.return_value = CompletedProcess(
        "", 0, stdout="\n".join(["  not-me", "* me", "  not-me-2"]).encode()
    )
    console_env = console.RealConsoleEnv()
    # when
    result = repo.get_local_branch_name(console_env, git.RealGitEnv())
    # then
    assert result == GitBranchName("me")


def test_getRepoDetailsFromRemoteV() -> None:
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


def test_git_commit_stack() -> None:
    # given
    git_env = FakeGitEnv(
        responses={
            "log --no-color origin/remote-branch..HEAD": [
                """
commit d9c3765ee8c6a1dee34d623b78c50a38bc57201c (HEAD -> master)
Author: Paul Campbell <pcampbell@kemitix.net>
Date:   Sat Sep 3 19:12:34 2022 +0100

    models.Commit: rename field oid as hash_id

    oid is used by Github.

    zen-token:97123f3a

commit b7bcf5ebdb8b277e267e47ee87fb568e53a8df06
Author: Paul Campbell <pcampbell@kemitix.net>
Date:   Sat Sep 3 19:10:18 2022 +0100

    gitzen.branches: whitespace cleanup

    zen-token:db8b277e

commit 55b1cc72019cad0d9c392eef10b817d86378ea61
Author: Paul Campbell <pcampbell@kemitix.net>
Date:   Sat Sep 3 19:07:26 2022 +0100

    Add git.log()

    zen-token:d0d9c392

commit 6a42e3c56e657e0b93f99e570fbab10ec35a81f8
Author: Paul Campbell <pcampbell@kemitix.net>
Date:   Sat Sep 3 15:27:40 2022 +0100

    WIP Create stub repo.get_local_commit_stack()

    zen-token:e0b93f99

commit 47d8ed21feb4164499828a920e8d8df280392a51
Author: Paul Campbell <pcampbell@kemitix.net>
Date:   Sat Sep 3 15:22:11 2022 +0100

    Extract barnches.get_required_remote_branch()

    zen-token:d21feb41

commit 1f293d6cdc6ed3b1100aa21c9528e4fc5c608fa9
Author: Paul Campbell <pcampbell@kemitix.net>
Date:   Sat Sep 3 15:11:46 2022 +0100

    Rename as branches.validate_not_remote_pr()

    zen-token:d6cdc6ed
""".splitlines()
            ]
        }
    )
    remote = "origin"
    remote_branch = GitBranchName("remote-branch")
    console_env = console.RealConsoleEnv()
    # when
    result = repo.get_commit_stack(console_env, git_env, remote, remote_branch)
    # then
    assert result == [
        Commit(  # 1
            zen_token=ZenToken("d6cdc6ed"),
            hash=CommitHash("1f293d6cdc6ed3b1100aa21c9528e4fc5c608fa9"),
            headline=CommitTitle(
                "Rename as branches.validate_not_remote_pr()",
            ),
            body=CommitBody(""),
            wip=CommitWipStatus(False),
        ),
        Commit(  # 2
            zen_token=ZenToken("d21feb41"),
            hash=CommitHash("47d8ed21feb4164499828a920e8d8df280392a51"),
            headline=CommitTitle(
                "Extract barnches.get_required_remote_branch()",
            ),
            body=CommitBody(""),
            wip=CommitWipStatus(False),
        ),
        Commit(  # 3
            zen_token=ZenToken("e0b93f99"),
            hash=CommitHash("6a42e3c56e657e0b93f99e570fbab10ec35a81f8"),
            headline=CommitTitle(
                "WIP Create stub repo.get_local_commit_stack()",
            ),
            body=CommitBody(""),
            wip=CommitWipStatus(True),
        ),
        Commit(  # 4
            zen_token=ZenToken("d0d9c392"),
            hash=CommitHash("55b1cc72019cad0d9c392eef10b817d86378ea61"),
            headline=CommitTitle("Add git.log()"),
            body=CommitBody(""),
            wip=CommitWipStatus(False),
        ),
        Commit(  # 5
            zen_token=ZenToken("db8b277e"),
            hash=CommitHash("b7bcf5ebdb8b277e267e47ee87fb568e53a8df06"),
            headline=CommitTitle("gitzen.branches: whitespace cleanup"),
            body=CommitBody(""),
            wip=CommitWipStatus(False),
        ),
        Commit(  # 6
            zen_token=ZenToken("97123f3a"),
            hash=CommitHash("d9c3765ee8c6a1dee34d623b78c50a38bc57201c"),
            headline=CommitTitle("models.Commit: rename field oid as hash_id"),
            body=CommitBody("oid is used by Github."),
            wip=CommitWipStatus(False),
        ),
    ]
