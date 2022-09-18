import re
from typing import List

from gitzen import config, console, file, git, repo
from gitzen.commands.push import update_patches, update_pr_branches
from gitzen.models.commit_pr import CommitPr
from gitzen.types import GitBranchName, GitRootDir

from . import object_mother as om
from .fakes.repo_files import given_repo, show_status


def test_when_no_branch_then_create(tmp_path) -> None:
    """
    When there is no local pr branch to track the
    CommitPr, then a branch is created.
    """
    # given
    root_dir = GitRootDir(tmp_path)
    git_env = git.RealGitEnv()
    given_repo(git_env, root_dir)
    cfg = config.default_config(root_dir)
    commits = repo.get_commit_stack(
        console.RealConsoleEnv(),
        git_env,
        cfg.remote,
        GitBranchName("master"),
    )
    assert len(commits) == 2
    author = om.gen_gh_username()
    commit1 = commits[0]
    commit2 = commits[1]
    stack: List[CommitPr] = [CommitPr(commit1, None), CommitPr(commit2, None)]
    update_patches(root_dir, [commit1, commit2])
    show_status(git_env, root_dir)
    # when
    update_pr_branches(git_env, stack, author, cfg)
    # then
    show_status(git_env, root_dir)
    expected_branch1 = (
        "gitzen/pr"
        f"/{author.value}"
        f"/{cfg.default_remote_branch.value}"
        f"/{commit1.zen_token.value}"
    )
    assert (
        git.branch_exists(git_env, GitBranchName(expected_branch1)) is True
    ), "first branch"
    expected_branch2 = (
        "gitzen/pr"
        f"/{author.value}"
        f"/{commit1.zen_token.value}"
        f"/{commit2.zen_token.value}"
    )
    assert (
        git.branch_exists(git_env, GitBranchName(expected_branch2)) is True
    ), "second branch"


def test_when_branch_and_change_then_update(tmp_path) -> None:
    """
    When there is a local pr branch and the patch has been
    updated, then the branch is updated.
    """
    # given
    root_dir = GitRootDir(tmp_path)
    git_env = git.RealGitEnv()
    given_repo(git_env, root_dir)
    cfg = config.default_config(root_dir)
    commits = repo.get_commit_stack(
        console.RealConsoleEnv(),
        git_env,
        cfg.remote,
        GitBranchName("master"),
    )
    assert len(commits) == 2
    author = om.gen_gh_username()
    stack: List[CommitPr] = [CommitPr(commit, None) for commit in commits]
    update_patches(root_dir, commits)
    git.branch_create(
        git_env,
        GitBranchName(commits[1].zen_token.value),
        GitBranchName("master"),
    )
    file.write("new-file", ["contents"])
    git.add(git_env, ["new-file"])
    output = git.commit_amend_noedit(git_env)
    hash_match = False
    expected_hash = None
    for line in output:
        hash_match = re.search(
            r"^\[master (?P<short_hash>[a-f0-9]{7})\]",
            line,
        )
        if hash_match:
            expected_hash = hash_match.group("short_hash")
            break
    assert hash_match
    assert expected_hash is not None
    # when
    update_pr_branches(git_env, stack, author, cfg)
    # then
    expected_branch1 = (
        "gitzen/pr"
        f"/{author.value}"
        f"/{cfg.default_remote_branch.value}"
        f"/{commits[0].zen_token.value}"
    )
    [hash] = git.rev_parse(git_env, expected_branch1)
    assert hash.startswith(expected_hash)
    expected_branch2 = (
        "gitzen/pr"
        f"/{author.value}"
        f"/{commits[0].zen_token.value}"
        f"/{commits[1].zen_token.value}"
    )
    [hash] = git.rev_parse(git_env, expected_branch2)
    assert hash.startswith(expected_hash)


def test_when_branch_and_no_change_then_ignore(tmp_path) -> None:
    """
    When there is a local pr branch and the patch has not been
    updated, then ignore.
    """
    # given
    root_dir = GitRootDir(tmp_path)
    git_env = git.RealGitEnv()
    given_repo(git_env, root_dir)
    cfg = config.default_config(root_dir)
    commits = repo.get_commit_stack(
        console.RealConsoleEnv(),
        git_env,
        cfg.remote,
        GitBranchName("master"),
    )
    assert len(commits) == 2
    author = om.gen_gh_username()
    commit1 = commits[0]
    commit2 = commits[1]
    stack: List[CommitPr] = [CommitPr(commit1, None), CommitPr(commit2, None)]
    update_patches(root_dir, [commit1, commit2])
    update_pr_branches(git_env, stack, author, cfg)
    show_status(git_env, root_dir)
    # when
    update_pr_branches(git_env, stack, author, cfg)
    # then
    show_status(git_env, root_dir)
    expected_branch1 = (
        "gitzen/pr"
        f"/{author.value}"
        f"/{cfg.default_remote_branch.value}"
        f"/{commit1.zen_token.value}"
    )
    assert (
        git.branch_exists(git_env, GitBranchName(expected_branch1)) is True
    ), "first branch"
    expected_branch2 = (
        "gitzen/pr"
        f"/{author.value}"
        f"/{commit1.zen_token.value}"
        f"/{commit2.zen_token.value}"
    )
    assert (
        git.branch_exists(git_env, GitBranchName(expected_branch2)) is True
    ), "second branch"
