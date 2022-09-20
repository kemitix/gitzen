from subprocess import PIPE, STDOUT
from unittest import mock

from gitzen import console, github

from . import object_mother as om


@mock.patch("subprocess.run")
def test_invokes_command(mock_subproc_run) -> None:
    # given
    pr_branch = om.gen_git_branch_name()
    base = om.gen_git_branch_name()
    commit = om.gen_commit(token=None)
    # when
    console_env = console.RealConsoleEnv()
    github_env = github.RealGithubEnv()
    github.update_pull_request(
        console_env,
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
            commit.messageBody.value,
        ],
        stdout=PIPE,
        stderr=STDOUT,
    )
