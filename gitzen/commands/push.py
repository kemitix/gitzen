import re
from typing import Dict, List, Optional, Tuple

from gitzen import branches, config, envs, exit_code, git, github, repo
from gitzen.config import Config
from gitzen.console import say
from gitzen.envs import ConsoleEnv, GitEnv, GithubEnv
from gitzen.models.commit_pr import CommitPr
from gitzen.models.git_commit import GitCommit
from gitzen.models.git_patch import GitPatch
from gitzen.models.github_info import GithubInfo
from gitzen.models.github_pull_request import PullRequest
from gitzen.types import GitBranchName, GithubUsername, GitRootDir, ZenToken


def push(
    console_env: envs.ConsoleEnv,
    git_env: envs.GitEnv,
    github_env: envs.GithubEnv,
    cfg: config.Config,
) -> None:
    status, commit_stack = prepare_pr_branches(
        console_env,
        git_env,
        github_env,
        cfg,
    )
    publish_pr_branches(git_env, commit_stack, status.username, cfg)


def prepare_pr_branches(
    console_env: ConsoleEnv,
    git_env: GitEnv,
    github_env: GithubEnv,
    cfg: Config,
) -> Tuple[GithubInfo, List[CommitPr]]:
    status, commit_stack = prepare_patches(
        console_env,
        git_env,
        github_env,
        cfg,
    )
    update_pr_branches(
        console_env,
        git_env,
        commit_stack,
        status.username,
        cfg,
    )
    return status, commit_stack


def prepare_patches(
    console_env: ConsoleEnv,
    git_env: GitEnv,
    github_env: GithubEnv,
    cfg: Config,
) -> Tuple[GithubInfo, List[CommitPr]]:
    status = github.fetch_info(console_env, git_env, github_env)
    local_branch = status.local_branch
    say(console_env, f"local branch: {local_branch.value}")
    remote_branch = branches.get_required_remote_branch(
        console_env,
        local_branch,
        cfg,
    )
    remote_target = GitBranchName(f"{cfg.remote.value}/{remote_branch.value}")
    say(console_env, remote_target.value)
    git.fetch(git_env, cfg.remote)
    git.rebase(git_env, remote_target)
    branches.validate_not_remote_pr(console_env, local_branch)
    commits = repo.get_commit_stack(
        console_env,
        git_env,
        cfg.remote,
        remote_branch,
    )
    commit_stack = clean_up_deleted_commits(
        github_env,
        status.pull_requests,
        commits,
        cfg.root_dir,
    )
    pr_count = len(commit_stack)
    new_commits = [CommitPr(commit, None) for commit in commits[pr_count:]]
    commit_stack.extend(new_commits)
    update_patches(cfg.root_dir, commits)
    return status, commit_stack
    # TODO update pr base ref to last_pr head_ref if not already set to that
    # TODO create missing prs setting pr bases to previous pr head
    # TODO call git zen status


def clean_up_deleted_commits(
    github_env: envs.GithubEnv,
    pull_requests: List[PullRequest],
    commits: List[GitCommit],
    root_dir: GitRootDir,
) -> List[CommitPr]:
    """
    Any PR that has a zen-token that isn't in the current commit stack
    is closed as the commit has gone away.
    Issue: if commit is on another branch?
    """
    zen_tokens: Dict[ZenToken, GitCommit] = {}
    for commit in commits:
        zen_tokens[commit.zen_token] = commit
    kept: List[CommitPr] = []
    for pr in pull_requests:
        if pr.zen_token not in zen_tokens:
            github.close_pull_request_with_comment(
                github_env, pr, "Closing pull request: commit has gone away"
            )
            git.delete_patch(pr.zen_token, root_dir)
        else:
            commit = zen_tokens[pr.zen_token]
            kept.append(CommitPr(commit, pr))
    return kept


def update_patches(
    root_dir: GitRootDir,
    commits: List[GitCommit],
) -> None:
    for commit in commits:
        patch = GitPatch(commit.zen_token, commit.hash)
        git.write_patch(patch, root_dir)


def update_pr_branches(
    console_env: envs.ConsoleEnv,
    git_env: envs.GitEnv,
    commit_stack: List[CommitPr],
    author: GithubUsername,
    cfg: config.Config,
    last_pr: Optional[PullRequest] = None,
) -> None:
    commit_pr = commit_stack[0]
    commit = commit_pr.git_commit
    pr = commit_pr.pull_request
    if pr is None:
        branch = create_pr_branch(
            git_env,
            last_pr,
            cfg,
            author,
            commit.zen_token,
        )
        cherry_pick_branch(console_env, git_env, commit.zen_token, branch)
        pr = PullRequest.create_template(commit, author, cfg, branch)
    else:
        update_pr_branch(console_env, git_env, pr, cfg, last_pr)
    if len(commit_stack) > 1:
        update_pr_branches(
            console_env,
            git_env,
            commit_stack[1:],
            author,
            cfg,
            pr,
        )


def pr_source(
    last_pr: Optional[PullRequest],
    cfg: config.Config,
) -> GitBranchName:
    if last_pr is None:
        source = cfg.default_remote_branch
    else:
        source = GitBranchName(last_pr.zen_token.value)
    return source


def create_pr_branch(
    git_env: envs.GitEnv,
    last_pr: Optional[PullRequest],
    cfg: config.Config,
    author: GithubUsername,
    zen_token: ZenToken,
) -> GitBranchName:
    source = pr_source(last_pr, cfg)
    branch = branches.pr_branch_planned(
        author,
        source,
        zen_token,
    )
    if last_pr is None:
        source_branch = GitBranchName(
            f"{cfg.remote.value}/{cfg.default_remote_branch.value}"
        )
    else:
        source_branch = branches.pr_branch(last_pr)
    git.branch_create(git_env, branch, source_branch)
    return branch


def update_pr_branch(
    console_env: envs.ConsoleEnv,
    git_env: envs.GitEnv,
    pr: PullRequest,
    cfg: config.Config,
    last_pr: Optional[PullRequest],
) -> None:
    branch_name = branches.pr_branch(pr)
    if git.branch_exists(git_env, branch_name):
        cherry_pick_branch(console_env, git_env, pr.zen_token, branch_name)
    else:
        branch = create_pr_branch(
            git_env,
            last_pr,
            cfg,
            pr.author,
            pr.zen_token,
        )
        cherry_pick_branch(console_env, git_env, pr.zen_token, branch)


def cherry_pick_branch(
    console_env: envs.ConsoleEnv,
    git_env: envs.GitEnv,
    zen_token: ZenToken,
    branch: GitBranchName,
) -> None:
    patch_ref = git.gitzen_patch_ref(zen_token)
    original_branch = repo.get_local_branch_name(console_env, git_env)
    git.switch(git_env, branch)
    git.status(git_env)
    status = git.cherry_pick(git_env, patch_ref)
    git.status(git_env)
    empty_cherry_pick_message = (
        "The previous cherry-pick is now empty, "
        + "possibly due to conflict resolution."
    )
    if empty_cherry_pick_message in status:
        git.cherry_pick_skip(git_env)
        git.status(git_env)
    for line in status:
        conflict_match = re.search(
            r"^CONFLICT \(content\): Merge conflict in (?P<filename>.*)\s*$",
            line,
        )
        if conflict_match:
            print("Error: merge conflict preparing PR branch")
            exit(exit_code.CONFLICT_PREPARING_PR_BRANCH)
    git.switch(git_env, original_branch)


def publish_pr_branches(
    git_env: envs.GitEnv,
    commit_stack: List[CommitPr],
    author: GithubUsername,
    cfg: config.Config,
    last_base_branch: Optional[GitBranchName] = None,
) -> None:
    if len(commit_stack) == 0:
        return
    if last_base_branch is None:
        base_branch = cfg.default_remote_branch
    else:
        base_branch = last_base_branch
    commit_pr = commit_stack[0]
    commit = commit_pr.git_commit
    pr_branch = branches.pr_branch_planned(
        author,
        base_branch,
        commit.zen_token,
    )
    git.push(git_env, cfg.remote, pr_branch)
    publish_pr_branches(
        git_env,
        commit_stack[1:],
        author,
        cfg,
        GitBranchName(commit.zen_token.value),
    )
