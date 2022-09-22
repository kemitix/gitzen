import re
from pathlib import PosixPath

from gitzen import config, console, file, git, logger, repo
from gitzen.commands.push import prepare_pr_branches, update_pr_branches
from gitzen.patterns import short_hash
from gitzen.types import GitBranchName

from . import object_mother as om
from .fakes.github_env import FakeGithubEnv
from .fakes.repo_files import given_repo


def test_when_no_branch_then_create(tmp_path: PosixPath) -> None:
    """
    When there is no local pr branch to track the
    CommitPr, then a branch is created.
    """
    # given
    logger_env = logger.RealEnv()
    file_env = file.RealEnv(logger_env)
    git_env = git.RealEnv(logger_env)
    root_dir = given_repo(file_env, git_env, tmp_path)
    cfg = config.default_config(root_dir)
    repo_id = om.gen_gh_repo_id()
    login = om.gen_gh_username()
    github_env = FakeGithubEnv(
        gh_responses={},
        gql_responses={
            repr({"repo_owner": "{owner}", "repo_name": "{repo}"}): [
                {
                    "data": {
                        "repository": {"id": repo_id.value},
                        "viewer": {
                            "login": login.value,
                            "repository": {
                                "pullRequests": {
                                    "nodes": [],
                                },
                            },
                        },
                    }
                },
                {
                    "data": {
                        "repository": {"id": repo_id.value},
                        "viewer": {
                            "login": login.value,
                            "repository": {
                                "pullRequests": {
                                    "nodes": [],
                                },
                            },
                        },
                    }
                },
            ]
        },
    )
    console_env = console.RealEnv()
    commits = repo.get_commit_stack(
        console.RealEnv(),
        git_env,
        cfg.remote,
        GitBranchName("master"),
    )
    assert len(commits) == 2
    token1 = commits[0].zen_token
    token2 = commits[1].zen_token
    (_, stack) = prepare_pr_branches(
        console_env,
        file_env,
        git_env,
        github_env,
        cfg,
    )
    # when
    update_pr_branches(console_env, git_env, stack)
    # then
    assert (
        git.branch_exists(
            git_env,
            GitBranchName(f"gitzen/pr/{login.value}/master/{token1.value}"),
        )
        is True
    ), "first branch"
    assert (
        git.branch_exists(
            git_env,
            GitBranchName(
                f"gitzen/pr/{login.value}/{token1.value}/{token2.value}",
            ),
        )
        is True
    ), "second branch"


def test_when_branch_and_change_then_update(tmp_path: PosixPath) -> None:
    """
    When there is a local pr branch and the patch has been
    updated, then the branch is updated.
    """
    # given
    logger_env = logger.RealEnv()
    file_env = file.RealEnv(logger_env)
    git_env = git.RealEnv(logger_env)
    root_dir = given_repo(file_env, git_env, tmp_path)
    repo_id = om.gen_gh_repo_id()
    login = om.gen_gh_username()
    github_env = FakeGithubEnv(
        gh_responses={},
        gql_responses={
            repr({"repo_owner": "{owner}", "repo_name": "{repo}"}): [
                {
                    "data": {
                        "repository": {"id": repo_id.value},
                        "viewer": {
                            "login": login.value,
                            "repository": {
                                "pullRequests": {
                                    "nodes": [],
                                },
                            },
                        },
                    }
                },
                {
                    "data": {
                        "repository": {"id": repo_id.value},
                        "viewer": {
                            "login": login.value,
                            "repository": {
                                "pullRequests": {
                                    "nodes": [],
                                },
                            },
                        },
                    }
                },
            ]
        },
    )
    console_env = console.RealEnv()
    cfg = config.default_config(root_dir)

    console.info(console_env, "prepare initial pr branches")
    prepare_pr_branches(console_env, file_env, git_env, github_env, cfg)

    console.info(console_env, "Add new-file")
    file.write(file_env, "new-file", ["contents"])
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
    console.info(console_env, "prepare new pr branches")
    status, stack = prepare_pr_branches(
        console_env,
        file_env,
        git_env,
        github_env,
        cfg,
    )
    # then
    console.info(console_env, "Review status")
    log = git.log_graph(git_env)
    assert len(log) == 7
    if "HEAD" in log[0]:
        patch_beta = 0
        patch_alpha = 1
        pull_beta = 2
        pull_alpha = 4
    else:
        pull_beta = 0
        pull_alpha = 2
        patch_beta = 3
        patch_alpha = 4
    author = status.username.value
    token_alpha = stack[0].git_commit.zen_token
    token_beta = stack[1].git_commit.zen_token
    ref_patch_alpha = f"refs/gitzen/patches/{token_alpha.value}"
    ref_patch_beta = f"refs/gitzen/patches/{token_beta.value}"
    pr_alpha = f"gitzen/pr/{author}/master/{token_alpha.value}"
    pr_beta = f"gitzen/pr/{author}/{token_alpha.value}/{token_beta.value}"

    assert re.search(
        rf"\* {short_hash} \(HEAD -> master, {ref_patch_beta}\) Add BETA.md$",
        log[patch_beta],
    ), "Patch Beta"
    assert re.search(
        rf"\* {short_hash} \({ref_patch_alpha}\) Add ALPHA.md$",
        log[patch_alpha],
    ), "Patch Alpha"
    assert re.search(
        rf"\* {short_hash} \({pr_beta}\) Add BETA.md",
        log[pull_beta],
    ), "PR Beta"
    assert re.search(
        rf"\* {short_hash} \({pr_alpha}\) Add ALPHA.md",
        log[pull_alpha],
    ), "PR Alpha"


def test_when_branch_and_no_change_then_ignore(tmp_path: PosixPath) -> None:
    """
    When there is a local pr branch and the patch has not been
    updated, then ignore.
    """
    # given
    logger_env = logger.RealEnv()
    file_env = file.RealEnv(logger_env)
    git_env = git.RealEnv(logger_env)
    root_dir = given_repo(file_env, git_env, tmp_path)
    cfg = config.default_config(root_dir)
    repo_id = om.gen_gh_repo_id()
    login = om.gen_gh_username()
    github_env = FakeGithubEnv(
        gh_responses={},
        gql_responses={
            repr({"repo_owner": "{owner}", "repo_name": "{repo}"}): [
                {
                    "data": {
                        "repository": {"id": repo_id.value},
                        "viewer": {
                            "login": login.value,
                            "repository": {
                                "pullRequests": {
                                    "nodes": [],
                                },
                            },
                        },
                    }
                },
                {
                    "data": {
                        "repository": {"id": repo_id.value},
                        "viewer": {
                            "login": login.value,
                            "repository": {
                                "pullRequests": {
                                    "nodes": [],
                                },
                            },
                        },
                    }
                },
            ]
        },
    )
    console_env = console.RealEnv()
    commits = repo.get_commit_stack(
        console.RealEnv(),
        git_env,
        cfg.remote,
        GitBranchName("master"),
    )
    assert len(commits) == 2
    token1 = commits[0].zen_token
    token2 = commits[1].zen_token
    (_, stack) = prepare_pr_branches(
        console_env,
        file_env,
        git_env,
        github_env,
        cfg,
    )
    # when
    update_pr_branches(console_env, git_env, stack)
    # then
    assert (
        git.branch_exists(
            git_env,
            GitBranchName(f"gitzen/pr/{login.value}/master/{token1.value}"),
        )
        is True
    ), "first branch"
    assert (
        git.branch_exists(
            git_env,
            GitBranchName(
                f"gitzen/pr/{login.value}/{token1.value}/{token2.value}",
            ),
        )
        is True
    ), "second branch"
