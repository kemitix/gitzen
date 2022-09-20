from gitzen import console
from gitzen.commands.push import create_pr

from . import object_mother as om
from .fakes.github_env import MuteFakeGuthubEnv


def test_invokes_command() -> None:
    # given
    head = om.gen_git_branch_name()
    base = om.gen_git_branch_name()
    commit = om.gen_commit(token=None)
    console_env = console.RealConsoleEnv()
    github_env = MuteFakeGuthubEnv()
    # when
    create_pr(console_env, github_env, head, base, commit)
    # then
    assert len(github_env.requests) == 1
    assert github_env.requests[0] == (
        "pr create "
        f"--head {head.value} "
        f"--base {base.value} "
        f"--title '{commit.messageHeadline.value}' "
        f"--body '{commit.messageBody.value}'"
    )
