from gitzen import envs
from gitzen.commands import push
from gitzen.models.git_commit import GitCommit
from gitzen.models.github_commit import GithubCommit
from gitzen.models.github_pull_request import PullRequest
from gitzen.types import (
    CommitBody,
    CommitHash,
    CommitTitle,
    CommitWipStatus,
    GitBranchName,
    GithubRepoId,
    PullRequestBody,
    PullRequestId,
    PullRequestMergeable,
    PullRequestNumber,
    PullRequestReviewDecision,
    PullRequestTitle,
    ZenToken,
)

from .fakes.github_env import FakeGithubEnv


def test_clean_up_deleted_commits_closes_with_comment() -> None:
    # given
    close_123_args = (
        "pr close 123 --comment 'Closing pull request: commit has gone away'"
    )
    github_env: envs.GithubEnv = FakeGithubEnv(
        gh_responses={close_123_args: [[]]},
        gql_responses={},
    )
    pr_to_close: PullRequest = PullRequest(
        id=PullRequestId("abcd123"),
        zen_token=ZenToken("12341234"),
        number=PullRequestNumber("123"),
        title=PullRequestTitle("pr 123"),
        body=PullRequestBody("zen-token:12341234"),
        baseRefName=GitBranchName("base"),
        headRefName=GitBranchName("head"),
        mergeable=PullRequestMergeable("MERGEABLE"),
        reviewDecision=PullRequestReviewDecision("UNKNOWN"),
        repoId=GithubRepoId("foo"),
        commits=[],
    )
    zen_token = ZenToken("43214321")
    pr_to_keep = PullRequest(
        id=PullRequestId("def456"),
        zen_token=zen_token,
        number=PullRequestNumber("321"),
        title=PullRequestTitle("pr 321"),
        body=PullRequestBody("zen-token:43214321"),
        baseRefName=GitBranchName("base"),
        headRefName=GitBranchName("head"),
        mergeable=PullRequestMergeable("MERGEABLE"),
        reviewDecision=PullRequestReviewDecision("UNKNOWN"),
        repoId=GithubRepoId("foo"),
        commits=[
            GithubCommit(
                zen_token=zen_token,
                hash=CommitHash(""),
                headline=CommitTitle(""),
                body=CommitBody(""),
                wip=CommitWipStatus(False),
            )
        ],
    )
    prs = [pr_to_close, pr_to_keep]
    git_commits = [
        GitCommit(
            zen_token=zen_token,
            hash=CommitHash(""),
            headline=CommitTitle(""),
            body=CommitBody(""),
            wip=CommitWipStatus(False),
        )
    ]
    # when
    push.clean_up_deleted_commits(github_env, prs, git_commits)
    # then
    assert pr_to_close.number.value in github_env.closed_with_comment
    assert (
        github_env.closed_with_comment[pr_to_close.number.value]
        == "Closing pull request: commit has gone away"
    )


def test_clean_up_deleted_commits_returns_remaining_prs() -> None:
    # given
    close_123_args = (
        "pr close 123 --comment 'Closing pull request: commit has gone away'"
    )
    github_env: envs.GithubEnv = FakeGithubEnv(
        gh_responses={close_123_args: [[]]},
        gql_responses={},
    )
    pr_to_close: PullRequest = PullRequest(
        id=PullRequestId("abcd123"),
        zen_token=ZenToken("12341234"),
        number=PullRequestNumber("123"),
        title=PullRequestTitle("pr 123"),
        body=PullRequestBody("zen-token:12341234"),
        baseRefName=GitBranchName("base"),
        headRefName=GitBranchName("head"),
        mergeable=PullRequestMergeable("MERGEABLE"),
        reviewDecision=PullRequestReviewDecision("UNKNOWN"),
        repoId=GithubRepoId("foo"),
        commits=[],
    )
    zen_token = ZenToken("43214321")
    pr_to_keep: PullRequest = PullRequest(
        id=PullRequestId("def456"),
        zen_token=zen_token,
        number=PullRequestNumber("321"),
        title=PullRequestTitle("pr 321"),
        body=PullRequestBody("zen-token:43214321"),
        baseRefName=GitBranchName("base"),
        headRefName=GitBranchName("head"),
        mergeable=PullRequestMergeable("MERGEABLE"),
        reviewDecision=PullRequestReviewDecision("UNKNOWN"),
        repoId=GithubRepoId("foo"),
        commits=[
            GithubCommit(
                zen_token=zen_token,
                hash=CommitHash(""),
                headline=CommitTitle(""),
                body=CommitBody(""),
                wip=CommitWipStatus(False),
            )
        ],
    )
    prs = [pr_to_close, pr_to_keep]
    git_commits = [
        GitCommit(
            zen_token=zen_token,
            hash=CommitHash(""),
            headline=CommitTitle(""),
            body=CommitBody(""),
            wip=CommitWipStatus(False),
        )
    ]
    # when
    open_prs = push.clean_up_deleted_commits(github_env, prs, git_commits)
    # then
    assert open_prs == [pr_to_keep]


def test_reordered_when_too_many_commits() -> None:
    # given
    commits = [
        GitCommit(
            ZenToken("foo"),
            CommitHash(""),
            CommitTitle(""),
            CommitBody(""),
            CommitWipStatus(False),
        )
    ]
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
    git_commit_foo = GitCommit(
        ZenToken("foo"),
        CommitHash(""),
        CommitTitle(""),
        CommitBody(""),
        CommitWipStatus(False),
    )
    git_commit_bar = GitCommit(
        ZenToken("bar"),
        CommitHash(""),
        CommitTitle(""),
        CommitBody(""),
        CommitWipStatus(False),
    )
    commits = [git_commit_foo, git_commit_bar]
    prs = [
        PullRequest(
            PullRequestId(""),
            ZenToken(""),
            PullRequestNumber(""),
            PullRequestTitle(""),
            PullRequestBody(""),
            GitBranchName(""),
            GitBranchName(""),
            PullRequestMergeable(""),
            PullRequestReviewDecision(""),
            GithubRepoId(""),
            [
                GithubCommit(
                    ZenToken("foo"),
                    CommitHash(""),
                    CommitTitle(""),
                    CommitBody(""),
                    CommitWipStatus(False),
                )
            ],
        ),
        PullRequest(
            PullRequestId(""),
            ZenToken(""),
            PullRequestNumber(""),
            PullRequestTitle(""),
            PullRequestBody(""),
            GitBranchName(""),
            GitBranchName(""),
            PullRequestMergeable(""),
            PullRequestReviewDecision(""),
            GithubRepoId(""),
            [
                GithubCommit(
                    ZenToken("bar"),
                    CommitHash(""),
                    CommitTitle(""),
                    CommitBody(""),
                    CommitWipStatus(False),
                )
            ],
        ),
    ]
    # when
    result = push.reordered(prs, commits)
    # then
    assert result is False


def test_reordered_when_reordered() -> None:
    # given
    git_commit_foo = GitCommit(
        ZenToken("foo"),
        CommitHash(""),
        CommitTitle(""),
        CommitBody(""),
        CommitWipStatus(False),
    )
    git_commit_bar = GitCommit(
        ZenToken("bar"),
        CommitHash(""),
        CommitTitle(""),
        CommitBody(""),
        CommitWipStatus(False),
    )
    commits = [git_commit_foo, git_commit_bar]
    prs = [
        PullRequest(
            PullRequestId(""),
            ZenToken(""),
            PullRequestNumber(""),
            PullRequestTitle(""),
            PullRequestBody(""),
            GitBranchName(""),
            GitBranchName(""),
            PullRequestMergeable(""),
            PullRequestReviewDecision(""),
            GithubRepoId(""),
            [
                GithubCommit(
                    ZenToken("bar"),
                    CommitHash(""),
                    CommitTitle(""),
                    CommitBody(""),
                    CommitWipStatus(False),
                )
            ],
        ),
        PullRequest(
            PullRequestId(""),
            ZenToken(""),
            PullRequestNumber(""),
            PullRequestTitle(""),
            PullRequestBody(""),
            GitBranchName(""),
            GitBranchName(""),
            PullRequestMergeable(""),
            PullRequestReviewDecision(""),
            GithubRepoId(""),
            [
                GithubCommit(
                    ZenToken("foo"),
                    CommitHash(""),
                    CommitTitle(""),
                    CommitBody(""),
                    CommitWipStatus(False),
                )
            ],
        ),
    ]
    # when
    result = push.reordered(prs, commits)
    # then
    assert result is True
