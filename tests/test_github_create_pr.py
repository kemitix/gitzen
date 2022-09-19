from subprocess import PIPE, STDOUT
from unittest import mock

from gitzen import github

from . import object_mother as om


@mock.patch("subprocess.run")
def test_invokes_command(mock_subproc_run) -> None:
    # given
    head = om.gen_git_branch_name()
    base = om.gen_git_branch_name()
    commit = om.gen_commit(token=None)
    # when
    github.create_pull_request(github.RealGithubEnv(), head, base, commit)
    # then
    mock_subproc_run.assert_called_with(
        [
            "gh",
            "pr",
            "create",
            "--head",
            head.value,
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
