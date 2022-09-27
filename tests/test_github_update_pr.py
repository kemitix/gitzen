from subprocess import PIPE, STDOUT
from unittest import mock

from gitzen import github, logger
from gitzen.models.git_commit import GitCommit
from gitzen.types import CommitWipStatus

from . import object_mother as om


@mock.patch("subprocess.run")
def test_invokes_command_has_token(mock_subproc_run) -> None:
    # given
    pr_branch = om.gen_git_branch_name()
    base = om.gen_git_branch_name()
    commit = om.gen_commit(token=None)
    # when
    logger_env = logger.RealEnv()
    github_env = github.RealEnv(logger_env)
    github.update_pull_request(
        github_env,
        pr_branch,
        base,
        commit,
    )
    # then
    mock_subproc_run.assert_called_with(
        [
            "gh",
            "pr",
            "edit",
            pr_branch.value,
            "--base",
            base.value,
            "--title",
            commit.messageHeadline.value,
            "--body",
            f"{commit.messageBody.value}",
        ],
        stdout=PIPE,
        stderr=STDOUT,
    )


@mock.patch("subprocess.run")
def test_invokes_command_no_token(mock_subproc_run) -> None:
    # given
    pr_branch = om.gen_git_branch_name()
    base = om.gen_git_branch_name()
    commit = GitCommit(
        om.gen_zen_token(),
        om.gen_commit_hash(),
        om.gen_commit_title(False),
        om.gen_commit_body(None),  # no token in body
        CommitWipStatus(False),
    )
    # when
    logger_env = logger.RealEnv()
    github_env = github.RealEnv(logger_env)
    github.update_pull_request(
        github_env,
        pr_branch,
        base,
        commit,
    )
    # then
    mock_subproc_run.assert_called_with(
        [
            "gh",
            "pr",
            "edit",
            pr_branch.value,
            "--base",
            base.value,
            "--title",
            commit.messageHeadline.value,
            "--body",
            (
                f"{commit.messageBody.value}"
                "\n\n"
                f"zen-token:{commit.zen_token.value}"
            ),
        ],
        stdout=PIPE,
        stderr=STDOUT,
    )
