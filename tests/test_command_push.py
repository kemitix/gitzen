from pathlib import PosixPath

from faker import Faker
from genericpath import exists

from gitzen import envs, file, git
from gitzen.commands import push
from gitzen.models.git_commit import GitCommit
from gitzen.models.git_patch import GitPatch
from gitzen.models.github_commit import GithubCommit
from gitzen.models.github_pull_request import PullRequest
from gitzen.types import (
    CommitBody,
    CommitHash,
    CommitTitle,
    CommitWipStatus,
    GitBranchName,
    GithubRepoId,
    GitRootDir,
    PullRequestBody,
    PullRequestId,
    PullRequestMergeable,
    PullRequestNumber,
    PullRequestReviewDecision,
    PullRequestTitle,
    ZenToken,
)

from .fakes.github_env import FakeGithubEnv
from .fakes.repo_files import given_repo


# trunk-ignore(flake8/E501)
def test_clean_up_deleted_commits_closes_with_comment(tmp_path: PosixPath) -> None:
    # given
    root_dir = GitRootDir(f"{tmp_path}")
    given_repo(root_dir)
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
    push.clean_up_deleted_commits(github_env, prs, git_commits, root_dir)
    # then
    assert pr_to_close.number.value in github_env.closed_with_comment
    assert (
        github_env.closed_with_comment[pr_to_close.number.value]
        == "Closing pull request: commit has gone away"
    )


# trunk-ignore(flake8/E501)
def test_clean_up_deleted_commits_returns_remaining_prs(tmp_path: PosixPath) -> None:
    # given
    root_dir = GitRootDir(f"{tmp_path}")
    given_repo(root_dir)
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
    open_prs = push.clean_up_deleted_commits(
        github_env,
        prs,
        git_commits,
        root_dir,
    )
    # then
    assert open_prs == [pr_to_keep]


def test_clean_up_deleted_commits_deletes_patches(tmp_path: PosixPath) -> None:
    # given
    root_dir = GitRootDir(f"{tmp_path}")
    given_repo(root_dir)
    close_123_args = (
        "pr close 123 --comment 'Closing pull request: commit has gone away'"
    )
    github_env: envs.GithubEnv = FakeGithubEnv(
        gh_responses={close_123_args: [[]]},
        gql_responses={},
    )
    fake = Faker()
    deleted_zen_token = ZenToken(fake.hexify("^^^^^^^^"))
    deleted_commit = GithubCommit(
        deleted_zen_token,
        CommitHash(fake.hexify("^^^^^^^^^^^^^^^^^")),
        CommitTitle(""),
        CommitBody(""),
        CommitWipStatus(False),
    )
    pr_to_close: PullRequest = PullRequest(
        id=PullRequestId("abcd123"),
        zen_token=deleted_zen_token,
        number=PullRequestNumber("123"),
        title=PullRequestTitle("pr 123"),
        body=PullRequestBody("zen-token:12341234"),
        baseRefName=GitBranchName("base"),
        headRefName=GitBranchName("head"),
        mergeable=PullRequestMergeable("MERGEABLE"),
        reviewDecision=PullRequestReviewDecision("UNKNOWN"),
        repoId=GithubRepoId("foo"),
        commits=[deleted_commit],
    )
    zen_token = ZenToken(fake.hexify("^^^^^^^^"))
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
            hash=CommitHash("abcdef1234567890"),
            headline=CommitTitle(""),
            body=CommitBody(""),
            wip=CommitWipStatus(False),
        )
    ]
    patch = GitPatch(deleted_zen_token, deleted_commit.hash)
    git.write_patch(patch, root_dir)
    patch_file = f"{git.gitzen_patches(root_dir)}/{patch.zen_token.value}"
    assert exists(patch_file)
    assert file.read(patch_file) == [deleted_commit.hash.value]
    # when
    push.clean_up_deleted_commits(github_env, prs, git_commits, root_dir)
    # then
    assert not exists(patch_file)


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
