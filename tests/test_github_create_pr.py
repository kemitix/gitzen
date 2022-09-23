from subprocess import PIPE, STDOUT
from unittest import mock

from gitzen import github, logger

from . import object_mother as om


@mock.patch("subprocess.run")
def test_invokes_command(mock_subproc_run) -> None:
    # given
    head = om.gen_git_branch_name()
    base = om.gen_git_branch_name()
    commit = om.gen_commit(token=None)
    # when
    logger_env = logger.RealEnv()
    github_env = github.RealEnv(logger_env)
    github.create_pull_request(github_env, head, base, commit)
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
            (
                f"{commit.messageBody.value}"
                "\n\n"
                f"zen-token:{commit.zen_token.value}"
            ),
        ],
        stdout=PIPE,
        stderr=STDOUT,
    )
