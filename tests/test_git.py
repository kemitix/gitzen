from subprocess import PIPE, CompletedProcess
from unittest import mock

from faker import Faker

from gitzen import git
from gitzen.types import GitBranchName, GitRemoteName, GitRootDir


@mock.patch("subprocess.run")
def test_branch(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # when
    git.branch(git.RealGitEnv())
    # then
    mock_subproc_run.assert_called_with(
        [
            "git",
            "branch",
            "--no-color",
        ],
        stdout=PIPE,
    )


@mock.patch("subprocess.run")
def test_branch_create(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # given
    fake = Faker()
    new_branch_name = GitBranchName(fake.word())
    source_branch_name = GitBranchName(fake.word())
    # when
    git.branch_create(git.RealGitEnv(), new_branch_name, source_branch_name)
    # then
    mock_subproc_run.assert_called_with(
        [
            "git",
            "branch",
            new_branch_name.value,
            source_branch_name.value,
        ],
        stdout=PIPE,
    )


@mock.patch("subprocess.run")
def test_cherry_pick(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # given
    fake = Faker()
    ref = GitBranchName(fake.hexify("^^^^^^^"))
    # when
    git.cherry_pick(git.RealGitEnv(), ref)
    # then
    mock_subproc_run.assert_called_with(
        ["git", "cherry-pick", "-x", ref.value],
        stdout=PIPE,
    )


@mock.patch("subprocess.run")
def test_cherry_pick_skip(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # when
    git.cherry_pick_skip(git.RealGitEnv())
    # then
    mock_subproc_run.assert_called_with(
        ["git", "cherry-pick", "--skip"],
        stdout=PIPE,
    )


@mock.patch("subprocess.run")
def test_fetch(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # given
    remote = GitRemoteName(Faker().word())
    # when
    git.fetch(git.RealGitEnv(), remote)
    # then
    gitFetch = ["git", "fetch", remote.value]
    mock_subproc_run.assert_called_with(gitFetch, stdout=PIPE)


@mock.patch("subprocess.run")
def test_log(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # when
    git.log(git.RealGitEnv(), "master..HEAD")
    # then
    gitFetch = ["git", "log", "--no-color", "master..HEAD"]
    mock_subproc_run.assert_called_with(gitFetch, stdout=PIPE)


@mock.patch("subprocess.run")
def test_remote(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # when
    git.remote(git.RealGitEnv())
    # then
    mock_subproc_run.assert_called_with(
        [
            "git",
            "remote",
            "--verbose",
        ],
        stdout=PIPE,
    )


@mock.patch("subprocess.run")
def test_rebase(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # when
    git.rebase(git.RealGitEnv(), GitBranchName("target/branch"))
    # then
    mock_subproc_run.assert_called_with(
        [
            "git",
            "rebase",
            "target/branch",
            "--autostash",
        ],
        stdout=PIPE,
    )


@mock.patch("subprocess.run")
def test_revParse(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # when
    git.rev_parse(git.RealGitEnv(), "--verify HEAD")
    # then
    mock_subproc_run.assert_called_with(
        ["git", "rev-parse", "--verify", "HEAD"], stdout=PIPE
    )


@mock.patch("subprocess.run")
def test_revParse_returns_value(mock_subproc_run) -> None:
    """
    Test that revParse returns the value
    """
    # given
    mock_subproc_run.return_value = CompletedProcess(
        "", 0, stdout="688881f74786d59ff397ef81efe1c137167f46b2".encode()
    )
    # when
    result = git.rev_parse(git.RealGitEnv())
    # then
    assert result == ["688881f74786d59ff397ef81efe1c137167f46b2"]


@mock.patch("subprocess.run")
def test_switch(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # given
    branch = GitBranchName(Faker().word())
    # when
    git.switch(git.RealGitEnv(), branch)
    # then
    mock_subproc_run.assert_called_with(
        [
            "git",
            "switch",
            branch.value,
        ],
        stdout=PIPE,
    )


@mock.patch("subprocess.run")
def test_root_dir(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # when
    git.root_dir(git.RealGitEnv())
    # then
    gitRevParse = ["git", "rev-parse", "--show-toplevel"]
    mock_subproc_run.assert_called_with(gitRevParse, stdout=PIPE)


@mock.patch("subprocess.run")
def test_root_dir_returns_path(mock_subproc_run) -> None:
    """
    Test that rootDir returns the directory
    """
    # given
    mock_subproc_run.return_value = CompletedProcess(
        "", 0, stdout="test-root-dir".encode()
    )
    # when
    result = git.root_dir(git.RealGitEnv())
    # then
    assert result == GitRootDir("test-root-dir")
