from typing import List

from gitzen.commands.push import rethread_stack
from gitzen.models.commit_branches import CommitBranches
from gitzen.models.commit_pr import CommitPr
from gitzen.types import GitBranchName

from . import object_mother as om


def test_rethread_empty() -> None:
    # given
    stack: List[CommitPr] = []
    author = om.gen_gh_username()
    # when
    result = rethread_stack(author, stack, GitBranchName("master"))
    # then
    assert result == []


def test_rethread_three() -> None:
    # given
    stack: List[CommitPr] = [
        CommitPr(om.gen_commit(token=None), pr=None),
        CommitPr(om.gen_commit(token=None), pr=None),
        CommitPr(om.gen_commit(token=None), pr=None),
    ]
    author = om.gen_gh_username()
    expected: List[CommitBranches] = [
        CommitBranches(
            stack[0].git_commit,
            GitBranchName("master"),
            GitBranchName(
                (
                    f"gitzen/pr/{author.value}"
                    f"/master/{stack[0].git_commit.zen_token.value}"
                )
            ),
            remote_target=GitBranchName("origin/master"),
        ),
        CommitBranches(
            stack[1].git_commit,
            GitBranchName(
                (
                    f"gitzen/pr/{author.value}"
                    f"/master/{stack[0].git_commit.zen_token.value}"
                )
            ),
            GitBranchName(
                (
                    f"gitzen/pr/{author.value}"
                    f"/{stack[0].git_commit.zen_token.value}"
                    f"/{stack[1].git_commit.zen_token.value}"
                )
            ),
        ),
        CommitBranches(
            stack[2].git_commit,
            GitBranchName(
                (
                    f"gitzen/pr/{author.value}"
                    f"/{stack[0].git_commit.zen_token.value}"
                    f"/{stack[1].git_commit.zen_token.value}"
                )
            ),
            GitBranchName(
                (
                    f"gitzen/pr/{author.value}"
                    f"/{stack[1].git_commit.zen_token.value}"
                    f"/{stack[2].git_commit.zen_token.value}"
                )
            ),
        ),
    ]
    # when
    result = rethread_stack(
        author,
        stack,
        GitBranchName("master"),
        remote_target=GitBranchName("origin/master"),
    )
    # then
    assert result == expected
