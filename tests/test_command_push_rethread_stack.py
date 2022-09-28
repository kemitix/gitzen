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
    token_1 = stack[0].git_commit.zen_token
    token_2 = stack[1].git_commit.zen_token
    token_3 = stack[2].git_commit.zen_token
    expected: List[CommitBranches] = [
        CommitBranches(
            stack[0].git_commit,
            GitBranchName("master"),
            GitBranchName(f"gitzen/pr/{author.value}/{token_1.value}"),
            remote_target=GitBranchName("origin/master"),
        ),
        CommitBranches(
            stack[1].git_commit,
            GitBranchName(f"gitzen/pr/{author.value}/{token_1.value}"),
            GitBranchName(f"gitzen/pr/{author.value}/{token_2.value}"),
        ),
        CommitBranches(
            stack[2].git_commit,
            GitBranchName(f"gitzen/pr/{author.value}/{token_2.value}"),
            GitBranchName(f"gitzen/pr/{author.value}/{token_3.value}"),
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
