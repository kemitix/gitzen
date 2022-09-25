from subprocess import PIPE, STDOUT, CompletedProcess
from unittest import mock

from faker import Faker

from gitzen import git, logger
from gitzen.types import GitBranchName, GitRemoteName, GitRootDir

from . import object_mother as om


@mock.patch("subprocess.run")
def test_branch(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # given
    mock_subproc_run.return_value = CompletedProcess("", 0)
    # when
    git.branch(git.RealEnv(logger.RealEnv()))
    # then
    mock_subproc_run.assert_called_with(
        [
            "git",
            "branch",
            "--no-color",
        ],
        check=True,
        stdout=PIPE,
        stderr=STDOUT,
    )


@mock.patch("subprocess.run")
def test_branch_exists_when_true(mock_subproc_run) -> None:
    # given
    branch = om.gen_git_branch_name()
    branches = [
        om.gen_git_branch_name(),
        branch,
        om.gen_git_branch_name(),
    ]
    lines = [f"  {branch.value}" for branch in branches]
    mock_subproc_run.return_value = CompletedProcess(
        "", 0, stdout="\n".join(lines).encode()
    )
    # when
    result = git.branch_exists(
        git.RealEnv(logger.RealEnv()),
        branch,
    )
    # then
    assert result is True


@mock.patch("subprocess.run")
def test_branch_exists_when_false(mock_subproc_run) -> None:
    # given
    branch = om.gen_git_branch_name()
    branches = [
        om.gen_git_branch_name(),
        om.gen_git_branch_name(),
    ]
    lines = [f"  {branch.value}" for branch in branches]
    mock_subproc_run.return_value = CompletedProcess(
        "", 0, stdout="\n".join(lines).encode()
    )
    # when
    result = git.branch_exists(
        git.RealEnv(logger.RealEnv()),
        branch,
    )
    # then
    assert result is False


@mock.patch("subprocess.run")
def test_branch_create(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # given
    fake = Faker()
    new_branch_name = GitBranchName(fake.word())
    source_branch_name = GitBranchName(fake.word())
    mock_subproc_run.return_value = CompletedProcess("", 0)
    # when
    git.branch_create(
        git.RealEnv(logger.RealEnv()),
        new_branch_name,
        source_branch_name,
    )
    # then
    mock_subproc_run.assert_called_with(
        [
            "git",
            "branch",
            new_branch_name.value,
            source_branch_name.value,
        ],
        check=True,
        stdout=PIPE,
        stderr=STDOUT,
    )


@mock.patch("subprocess.run")
def test_cherry_pick(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # given
    fake = Faker()
    ref = GitBranchName(fake.hexify("^^^^^^^"))
    mock_subproc_run.return_value = CompletedProcess("", 0)
    # when
    git.cherry_pick(git.RealEnv(logger.RealEnv()), ref)
    # then
    mock_subproc_run.assert_called_with(
        [
            "git",
            "cherry-pick",
            "--allow-empty",
            "--allow-empty-message",
            "-x",
            ref.value,
        ],
        check=True,
        stdout=PIPE,
        stderr=STDOUT,
    )


@mock.patch("subprocess.run")
def test_cherry_pick_skip(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # given
    mock_subproc_run.return_value = CompletedProcess("", 0)
    # when
    git.cherry_pick_skip(git.RealEnv(logger.RealEnv()))
    # then
    mock_subproc_run.assert_called_with(
        ["git", "cherry-pick", "--skip"],
        check=True,
        stdout=PIPE,
        stderr=STDOUT,
    )


@mock.patch("subprocess.run")
def test_fetch(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # given
    remote = GitRemoteName(Faker().word())
    mock_subproc_run.return_value = CompletedProcess("", 0)
    # when
    git.fetch(git.RealEnv(logger.RealEnv()), remote)
    # then
    gitFetch = ["git", "fetch", remote.value]
    mock_subproc_run.assert_called_with(
        gitFetch,
        check=True,
        stdout=PIPE,
        stderr=STDOUT,
    )


@mock.patch("subprocess.run")
def test_log(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # given
    mock_subproc_run.return_value = CompletedProcess("", 0)
    # when
    git.log(git.RealEnv(logger.RealEnv()), "master..HEAD")
    # then
    gitFetch = ["git", "log", "--no-color", "master..HEAD"]
    mock_subproc_run.assert_called_with(
        gitFetch,
        check=True,
        stdout=PIPE,
        stderr=STDOUT,
    )


@mock.patch("subprocess.run")
def test_push(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # given
    remote = om.gen_remote_name()
    branch = om.gen_git_branch_name()
    mock_subproc_run.return_value = CompletedProcess("", 0)
    # when
    git.push(git.RealEnv(logger.RealEnv()), remote, branch)
    # then
    mock_subproc_run.assert_called_with(
        ["git", "push", remote.value, f"{branch.value}:{branch.value}"],
        check=True,
        stdout=PIPE,
        stderr=STDOUT,
    )


@mock.patch("subprocess.run")
def test_remote(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # given
    mock_subproc_run.return_value = CompletedProcess("", 0)
    # when
    git.remote(git.RealEnv(logger.RealEnv()))
    # then
    mock_subproc_run.assert_called_with(
        [
            "git",
            "remote",
            "--verbose",
        ],
        check=True,
        stdout=PIPE,
        stderr=STDOUT,
    )


@mock.patch("subprocess.run")
def test_rebase(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # given
    mock_subproc_run.return_value = CompletedProcess("", 0)
    # when
    git.rebase(
        git.RealEnv(logger.RealEnv()),
        GitBranchName("target/branch"),
    )
    # then
    mock_subproc_run.assert_called_with(
        [
            "git",
            "rebase",
            "target/branch",
            "--autostash",
        ],
        check=True,
        stdout=PIPE,
        stderr=STDOUT,
    )


@mock.patch("subprocess.run")
def test_revParse(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # given
    mock_subproc_run.return_value = CompletedProcess("", 0)
    # when
    git.rev_parse(git.RealEnv(logger.RealEnv()), "--verify HEAD")
    # then
    mock_subproc_run.assert_called_with(
        ["git", "rev-parse", "--verify", "HEAD"],
        check=True,
        stdout=PIPE,
        stderr=STDOUT,
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
    result = git.rev_parse(git.RealEnv(logger.RealEnv()))
    # then
    assert result == ["688881f74786d59ff397ef81efe1c137167f46b2"]


@mock.patch("subprocess.run")
def test_switch(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # given
    branch = GitBranchName(Faker().word())
    mock_subproc_run.return_value = CompletedProcess("", 0)
    # when
    git.switch(git.RealEnv(logger.RealEnv()), branch)
    # then
    mock_subproc_run.assert_called_with(
        [
            "git",
            "switch",
            branch.value,
        ],
        check=True,
        stdout=PIPE,
        stderr=STDOUT,
    )


@mock.patch("subprocess.run")
def test_root_dir(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # given
    mock_subproc_run.return_value = CompletedProcess(
        "",
        0,
        stdout="root_dir".encode(),
    )
    # when
    git.root_dir(git.RealEnv(logger.RealEnv()))
    # then
    gitRevParse = ["git", "rev-parse", "--show-toplevel"]
    mock_subproc_run.assert_called_with(
        gitRevParse,
        check=True,
        stdout=PIPE,
        stderr=STDOUT,
    )


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
    result = git.root_dir(git.RealEnv(logger.RealEnv()))
    # then
    assert result == GitRootDir("test-root-dir")
