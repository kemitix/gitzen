from pathlib import PosixPath

from genericpath import exists

from gitzen import console, file, git, logger
from gitzen.commands import push
from gitzen.models.git_patch import GitPatch
from gitzen.models.github_pull_request import PullRequest

from . import object_mother as om
from .fakes.github_env import FakeGithubEnv
from .fakes.repo_files import given_repo


# trunk-ignore(flake8/E501)
def test_clean_up_deleted_commits_closes_with_comment(tmp_path: PosixPath) -> None:
    # given
    logger_env = logger.RealEnv()
    console_env = console.RealEnv()
    file_env = file.RealEnv(logger_env)
    git_env = git.RealEnv(logger_env)
    root_dir, _ = given_repo(file_env, git_env, tmp_path)
    pr_to_close: PullRequest = om.gen_pr(token=None)
    zen_token = om.gen_zen_token()
    pr_to_keep = om.gen_pr(zen_token)
    prs = [pr_to_close, pr_to_keep]
    git_commits = [om.gen_commit(zen_token)]
    close_args = (
        f"pr close {pr_to_close.number.value} "
        "--comment 'Closing pull request: commit has gone away'"
    )
    github_env = FakeGithubEnv(
        gh_responses={close_args: [[]]},
        gql_responses={},
    )
    # when
    push.clean_up_deleted_commits(
        console_env,
        git_env,
        github_env,
        prs,
        git_commits,
        root_dir,
    )
    # then
    assert pr_to_close.number.value in github_env.closed_with_comment
    assert (
        github_env.closed_with_comment[pr_to_close.number.value]
        == "Closing pull request: commit has gone away"
    )


# trunk-ignore(flake8/E501)
def test_clean_up_deleted_commits_returns_remaining_prs(tmp_path: PosixPath) -> None:
    # given
    logger_env = logger.RealEnv()
    console_env = console.RealEnv()
    file_env = file.RealEnv(logger_env)
    git_env = git.RealEnv(logger_env)
    root_dir, _ = given_repo(file_env, git_env, tmp_path)
    pr_to_close: PullRequest = om.gen_pr(token=None)
    zen_token = om.gen_zen_token()
    pr_to_keep = om.gen_pr(zen_token)
    prs = [pr_to_close, pr_to_keep]
    git_commits = [om.gen_commit(zen_token)]
    close_args = (
        f"pr close {pr_to_close.number.value} "
        "--comment 'Closing pull request: commit has gone away'"
    )
    github_env = FakeGithubEnv(
        gh_responses={close_args: [[]]},
        gql_responses={},
    )
    # when
    result = push.clean_up_deleted_commits(
        console_env,
        git_env,
        github_env,
        prs,
        git_commits,
        root_dir,
    )
    # then
    assert len(result) == 1
    assert result[0].git_commit.zen_token == zen_token
    result_pr = result[0].pull_request
    assert result_pr == pr_to_keep


def test_clean_up_deleted_commits_deletes_patches(tmp_path: PosixPath) -> None:
    # given
    logger_env = logger.RealEnv()
    console_env = console.RealEnv()
    file_env = file.RealEnv(logger_env)
    git_env = git.RealEnv(logger_env)
    root_dir, _ = given_repo(file_env, git_env, tmp_path)
    deleted_zen_token = om.gen_zen_token()
    pr_to_close: PullRequest = om.gen_pr(deleted_zen_token)
    deleted_commit = pr_to_close.commits[0]
    zen_token = om.gen_zen_token()
    pr_to_keep = om.gen_pr(zen_token)
    prs = [pr_to_close, pr_to_keep]
    git_commits = [om.gen_commit(zen_token)]
    patch = GitPatch(deleted_zen_token, deleted_commit.hash)
    git.write_patch(file_env, patch, root_dir)
    patch_file = f"{git.gitzen_patches(root_dir)}/{patch.zen_token.value}"
    assert exists(patch_file)
    assert file.read(file_env, patch_file) == [deleted_commit.hash.value]
    close_args = (
        f"pr close {pr_to_close.number.value} "
        "--comment 'Closing pull request: commit has gone away'"
    )
    github_env = FakeGithubEnv(
        gh_responses={close_args: [[]]},
        gql_responses={},
    )
    # when
    push.clean_up_deleted_commits(
        console_env,
        git_env,
        github_env,
        prs,
        git_commits,
        root_dir,
    )
    # then
    assert not exists(patch_file)
