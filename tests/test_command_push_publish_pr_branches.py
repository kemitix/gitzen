import re
from pathlib import PosixPath

from gitzen import config, console, file, git, logger, repo
from gitzen.commands.push import prepare_pr_branches, publish_pr_branches
from gitzen.patterns import short_hash
from gitzen.types import GitBranchName

from . import object_mother as om
from .fakes.github_env import FakeGithubEnv
from .fakes.repo_files import given_repo


def test_when_remote_exists_and_is_uptodate_then_do_nothing(
    tmp_path: PosixPath,
) -> None:
    # given
    logger_env = logger.RealEnv()
    file_env = file.RealEnv(logger_env)
    git_env = git.RealEnv(logger_env)
    root_dir = given_repo(file_env, git_env, tmp_path)
    cfg = config.default_config(root_dir)
    console_env = console.RealEnv()
    commits = repo.get_commit_stack(
        console.RealEnv(),
        git_env,
        cfg.remote,
        GitBranchName("master"),
    )
    repo_id = om.gen_gh_repo_id()
    assert len(commits) == 2
    author = om.gen_gh_username()
    github_env = FakeGithubEnv(
        {},
        {
            repr({"repo_owner": "{owner}", "repo_name": "{repo}"}): [
                {
                    "data": {
                        "repository": {"id": repo_id.value},
                        "viewer": {
                            "login": author.value,
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
    _, stack = prepare_pr_branches(
        console_env,
        file_env,
        git_env,
        github_env,
        cfg,
    )
    # when
    publish_pr_branches(console_env, git_env, stack, author, cfg)
    # then
    token_alpha = commits[0].zen_token
    token_beta = commits[1].zen_token
    username = author.value
    pr_alpha = f"gitzen/pr/{username}/master/{token_alpha.value}"
    pr_beta = f"gitzen/pr/{username}/{token_alpha.value}/{token_beta.value}"
    assert git.branch_exists(git_env, GitBranchName(pr_alpha))
    assert git.branch_exists(git_env, GitBranchName(pr_beta))
    log = git.log_graph(git_env)
    [print(f"LOG> {line}") for line in log]
    assert len(log) == 6
    if "HEAD" in log[0]:
        patch_beta = 0
        patch_alpha = 1
        pull_beta = 2
        pull_alpha = 3
    else:
        pull_beta = 0
        pull_alpha = 1
        patch_beta = 2
        patch_alpha = 3
    ref_patch_alpha = f"refs/gitzen/patches/{token_alpha.value}"
    ref_patch_beta = f"refs/gitzen/patches/{token_beta.value}"
    assert re.search(
        rf"\* {short_hash} \(HEAD -> master, {ref_patch_beta}\) Add BETA.md$",
        log[patch_beta],
    ), "Patch Beta"
    assert re.search(
        rf"\* {short_hash} \({ref_patch_alpha}\) Add ALPHA.md$",
        log[patch_alpha],
    ), "Patch Alpha"
    assert re.search(
        rf"\* {short_hash} \(origin/{pr_beta}, {pr_beta}\) Add BETA.md",
        log[pull_beta],
    ), "PR Beta"
    assert re.search(
        rf"\* {short_hash} \(origin/{pr_alpha}, {pr_alpha}\) Add ALPHA.md",
        log[pull_alpha],
    ), "PR Alpha"
