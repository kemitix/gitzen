from subprocess import PIPE, STDOUT
from unittest import mock

import pytest

from gitzen import exit_code, github, logger
from gitzen.models.git_commit import GitCommit
from gitzen.models.gitzen_error import GitZenError
from gitzen.types import CommitWipStatus

from . import object_mother as om


@mock.patch("subprocess.run")
def test_invokes_command_when_has_token(mock_subproc_run) -> None:
    # given
    head = om.gen_git_branch_name()
    base = om.gen_git_branch_name()
    commit = om.gen_commit(token=None)
    logger_env = logger.RealEnv()
    github_env = github.RealEnv(logger_env)
    # when
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
            f"{commit.messageBody.value}",
        ],
        stdout=PIPE,
        stderr=STDOUT,
    )


@mock.patch("subprocess.run")
def test_raises_error_when_no_token(mock_subproc_run) -> None:
    # given
    head = om.gen_git_branch_name()
    base = om.gen_git_branch_name()
    commit = GitCommit(
        om.gen_zen_token(),
        om.gen_commit_hash(),
        om.gen_commit_title(False),
        om.gen_commit_body(None),  # no token in body
        CommitWipStatus(False),
    )
    logger_env = logger.RealEnv()
    github_env = github.RealEnv(logger_env)
    # when
    with pytest.raises(GitZenError) as error:
        github.create_pull_request(github_env, head, base, commit)
    # then
    assert error.type == GitZenError
    assert error.value.exit_code == exit_code.ZEN_TOKENS_MISSING
