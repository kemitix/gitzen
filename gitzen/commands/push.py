from typing import Dict, List, Optional

from gitzen import branches, config, envs, git, github, repo
from gitzen.console import say
from gitzen.models.commit_pr import CommitPr
from gitzen.models.git_commit import GitCommit
from gitzen.models.git_patch import GitPatch
from gitzen.models.github_pull_request import PullRequest
from gitzen.types import GitBranchName, GithubUsername, GitRootDir, ZenToken


def push(
    console_env: envs.ConsoleEnv,
    git_env: envs.GitEnv,
    github_env: envs.GithubEnv,
    cfg: config.Config,
) -> None:
    status = github.fetch_info(console_env, git_env, github_env)
    local_branch = status.local_branch
    say(console_env, f"local branch: {local_branch.value}")
    remote_branch = branches.get_required_remote_branch(
        console_env, local_branch, config
    )
    remote_target = GitBranchName(
        f"remote branch: {cfg.remote.value}/{remote_branch.value}"
    )
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
    say(console_env, repr(commits))
    commit_stack = clean_up_deleted_commits(
        github_env,
        status.pull_requests,
        commits,
        cfg.root_dir,
    )
    pr_count = len(commit_stack)
    new_commits = [CommitPr(commit, None) for commit in commits[pr_count:]]
    commit_stack.extend(new_commits)
    # check_for_reordered_commits(git_env, open_prs, commits)
    update_patches(cfg.root_dir, commits)
    update_pr_branches(git_env, commit_stack, status.username, cfg)
    # call git zen status


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
    git_env: envs.GitEnv,
    commit_stack: List[CommitPr],
    author: GithubUsername,
    config: config.Config,
    last_pr: Optional[PullRequest] = None,
) -> None:
    commit_pr = commit_stack[0]
    commit = commit_pr.git_commit
    pr = commit_pr.pull_request
    if pr is None:
        branch = create_pr_branch(
            git_env,
            last_pr,
            config,
            author,
            commit.zen_token,
        )
        cherry_pick_push_branch(git_env, commit.zen_token, branch)
    else:
        update_pr_branch(git_env, pr, config, last_pr)
    if len(commit_stack) > 1:
        update_pr_branches(git_env, commit_stack[1:], author, config, pr)


def pr_source(
    last_pr: Optional[PullRequest],
    config: config.Config,
) -> GitBranchName:
    if last_pr is None:
        source = config.default_remote_branch
    else:
        source = last_pr.headRefName
    return source


def create_pr_branch(
    git_env: envs.GitEnv,
    last_pr: Optional[PullRequest],
    config: config.Config,
    author: GithubUsername,
    zen_token: ZenToken,
) -> GitBranchName:
    source = pr_source(last_pr, config)
    branch = branches.pr_branch_planned(
        author,
        source,
        zen_token,
    )
    git.branch_create(git_env, branch, source)
    return branch


def update_pr_branch(
    git_env: envs.GitEnv,
    pr: PullRequest,
    config: config.Config,
    last_pr: Optional[PullRequest],
) -> None:
    branch_name = branches.pr_branch(pr)
    if git.branch_exists(git_env, branch_name):
        cherry_pick_push_branch(git_env, pr.zen_token, branch_name)
    else:
        branch = create_pr_branch(
            git_env,
            last_pr,
            config,
            pr.author,
            pr.zen_token,
        )
        cherry_pick_push_branch(git_env, pr.zen_token, branch)


def cherry_pick_push_branch(
    git_env: envs.GitEnv,
    zen_token: ZenToken,
    branch: GitBranchName,
) -> None:
    patch_ref = git.gitzen_patch_ref(zen_token)
    git.switch(git_env, branch)
    status = git.cherry_pick(git_env, patch_ref)
    if '  (all conflicts fixed: run "git cherry-pick --continue")' in status:
        git.cherry_pick_skip(git_env)


# TODO push PR branches to github
# TODO update PR base ref to last_pr head_ref if not already set to that
