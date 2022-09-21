from gitzen.commands.push import update_pr

from . import object_mother as om
from .fakes.github_env import MuteFakeGuthubEnv


def test_invokes_command() -> None:
    # given
    pr_branch = om.gen_git_branch_name()
    base = om.gen_git_branch_name()
    commit = om.gen_commit(token=None)
    github_env = MuteFakeGuthubEnv()
    # when
    update_pr(github_env, pr_branch, base, commit)
    # then
    # assert len(github_env.requests) == 1
    assert github_env.requests == [
        (
            "pr edit "
            f"{pr_branch.value} "
            f"--base {base.value} "
            f"--title '{commit.messageHeadline.value}' "
            f"--body '{commit.messageBody.value}'"
        )
    ]
