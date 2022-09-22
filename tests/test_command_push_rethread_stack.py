from typing import List

from gitzen.commands.push import rethread_stack
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
        om.gen_commit_pr(),
        om.gen_commit_pr(),
        om.gen_commit_pr(),
    ]
    author = om.gen_gh_username()
    expected: List[CommitPr] = [
        CommitPr(
            stack[0].git_commit,
            stack[0].pull_request,
            GitBranchName("master"),
            GitBranchName(
                (
                    f"gitzen/pr/{author.value}"
                    f"/master/{stack[0].git_commit.zen_token.value}"
                )
            ),
        ),
        CommitPr(
            stack[1].git_commit,
            stack[1].pull_request,
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
        CommitPr(
            stack[2].git_commit,
            stack[2].pull_request,
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
    result = rethread_stack(author, stack, GitBranchName("master"))
    # then
    assert result == expected
