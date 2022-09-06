from gitzen import envs
from gitzen.commands import push
from gitzen.models.github_commit import Commit
from gitzen.models.github_pull_request import PullRequest

from .fakes.github_env import FakeGithubEnv


def test_close_prs_for_deleted_commits_closes_with_comment() -> None:
    # given
    github_env: envs.GithubEnv = FakeGithubEnv()
    pr_to_close: PullRequest = PullRequest(
        id="abcd123",
        zen_token="12341234",
        number="123",
        title="pr 123",
        body="zen-token:12341234",
        baseRefName="base",
        headRefName="head",
        mergeable="MERGEABLE",
        reviewDecision="UNKNOWN",
        repoId="foo",
        commits=[],
    )
    zen_token = "43214321"
    pr_to_keep: PullRequest = PullRequest(
        id="def456",
        zen_token=zen_token,
        number="321",
        title="pr 321",
        body="zen-token:43214321",
        baseRefName="base",
        headRefName="head",
        mergeable="MERGEABLE",
        reviewDecision="UNKNOWN",
        repoId="foo",
        commits=[
            Commit(
                zen_token=zen_token,
                hash="",
                headline="",
                body="",
                wip=False,
            )
        ],
    )
    prs = [pr_to_close, pr_to_keep]
    commits = pr_to_keep.commits
    # when
    push.close_prs_for_deleted_commits(github_env, prs, commits)
    # then
    assert pr_to_close.number in github_env.closed_with_comment
    assert (
        github_env.closed_with_comment[pr_to_close.number]
        == "Closing pull request: commit has gone away"
    )


def test_close_prs_for_deleted_commits_returns_remaining_prs() -> None:
    # given
    github_env: envs.GithubEnv = FakeGithubEnv()
    pr_to_close: PullRequest = PullRequest(
        id="abcd123",
        zen_token="12341234",
        number="123",
        title="pr 123",
        body="zen-token:12341234",
        baseRefName="base",
        headRefName="head",
        mergeable="MERGEABLE",
        reviewDecision="UNKNOWN",
        repoId="foo",
        commits=[],
    )
    zen_token = "43214321"
    pr_to_keep: PullRequest = PullRequest(
        id="def456",
        zen_token=zen_token,
        number="321",
        title="pr 321",
        body="zen-token:43214321",
        baseRefName="base",
        headRefName="head",
        mergeable="MERGEABLE",
        reviewDecision="UNKNOWN",
        repoId="foo",
        commits=[
            Commit(
                zen_token=zen_token,
                hash="",
                headline="",
                body="",
                wip=False,
            )
        ],
    )
    prs = [pr_to_close, pr_to_keep]
    commits = pr_to_keep.commits
    # when
    open_prs = push.close_prs_for_deleted_commits(github_env, prs, commits)
    # then
    assert open_prs == [pr_to_keep]


def test_reordered_when_too_many_commits() -> None:
    # given
    commits = [Commit("foo", "", "", "", False)]
    prs = []
    # when
    result = push.reordered(prs, commits)
    # then
    # for all the PRs, the commits were in the correct order,
    # there may be additional commits, but those will become
    # new PRs
    assert result is False


def test_reordered_when_not_reordered() -> None:
    # given
    commit_foo = Commit("foo", "", "", "", False)
    commit_bar = Commit("bar", "", "", "", False)
    commits = [commit_foo, commit_bar]
    prs = [
        PullRequest("", "", "", "", "", "", "", "", "", "", [commit_foo]),
        PullRequest("", "", "", "", "", "", "", "", "", "", [commit_bar]),
    ]
    # when
    result = push.reordered(prs, commits)
    # then
    assert result is False


def test_reordered_when_reordered() -> None:
    # given
    commit_foo = Commit("foo", "", "", "", False)
    commit_bar = Commit("bar", "", "", "", False)
    commits = [commit_foo, commit_bar]
    prs = [
        PullRequest("", "", "", "", "", "", "", "", "", "", [commit_bar]),
        PullRequest("", "", "", "", "", "", "", "", "", "", [commit_foo]),
    ]
    # when
    result = push.reordered(prs, commits)
    # then
    assert result is True
