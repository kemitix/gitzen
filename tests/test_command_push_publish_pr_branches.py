import re
from pathlib import PosixPath
from typing import List

from gitzen import config, console, file, git, repo

# trunk-ignore(flake8/E501)
from gitzen.commands.push import publish_pr_branches, update_patches, update_pr_branches
from gitzen.models.commit_pr import CommitPr
from gitzen.patterns import short_hash
from gitzen.types import GitBranchName

from . import object_mother as om
from .fakes.repo_files import given_repo


def test_when_remote_exists_and_is_uptodate_then_do_nothing(
    tmp_path: PosixPath,
) -> None:
    # given
    file_env = file.RealEnv()
    git_env = git.RealEnv()
    root_dir = given_repo(file_env, git_env, tmp_path)
    cfg = config.default_config(root_dir)
    console_env = console.RealEnv()
    commits = repo.get_commit_stack(
        console.RealEnv(),
        git_env,
        cfg.remote,
        GitBranchName("master"),
    )
    assert len(commits) == 2
    stack: List[CommitPr] = [CommitPr(commit, None) for commit in commits]
    author = om.gen_gh_username()
    update_patches(file_env, cfg.root_dir, commits)
    update_pr_branches(console_env, git_env, stack, author, cfg)
    # when
    publish_pr_branches(console_env, git_env, stack, author, cfg)
    # then
    token_alpha = commits[0].zen_token
    token_beta = commits[1].zen_token
    username = author.value
    pr_alpha = f"gitzen/pr/{username}/master/{token_alpha.value}"
    pr_beta = f"gitzen/pr/{username}/{token_alpha.value}/{token_beta.value}"
    assert git.branch_exists(console_env, git_env, GitBranchName(pr_alpha))
    assert git.branch_exists(console_env, git_env, GitBranchName(pr_beta))
    log = git.log_graph(console_env, git_env)
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
