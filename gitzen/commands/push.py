import re
from typing import Dict, List, Optional, Tuple

# trunk-ignore(flake8/E501)
from gitzen import branches, config, console, exit_code, file, git, github, repo
from gitzen.config import Config
from gitzen.console import info
from gitzen.models.commit_pr import CommitPr
from gitzen.models.git_commit import GitCommit
from gitzen.models.git_patch import GitPatch
from gitzen.models.github_info import GithubInfo
from gitzen.models.github_pull_request import PullRequest
from gitzen.types import GitBranchName, GithubUsername, GitRootDir, ZenToken


def push(
    console_env: console.Env,
    file_env: file.Env,
    git_env: git.Env,
    github_env: github.Env,
    cfg: config.Config,
) -> None:
    status, commit_stack = prepare_pr_branches(
        console_env,
        file_env,
        git_env,
        github_env,
        cfg,
    )
    publish_pr_branches(
        console_env,
        git_env,
        commit_stack,
        status.username,
        cfg,
    )
    regenerate_prs(console_env, github_env, commit_stack, status.username, cfg)


def prepare_pr_branches(
    console_env: console.Env,
    file_env: file.Env,
    git_env: git.Env,
    github_env: github.Env,
    cfg: Config,
) -> Tuple[GithubInfo, List[CommitPr]]:
    status, commit_stack = prepare_patches(
        console_env,
        file_env,
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
    console_env: console.Env,
    file_env: file.Env,
    git_env: git.Env,
    github_env: github.Env,
    cfg: Config,
) -> Tuple[GithubInfo, List[CommitPr]]:
    status = github.fetch_info(console_env, git_env, github_env)
    local_branch = status.local_branch
    info(console_env, f"local branch: {local_branch.value}")
    remote_branch = branches.get_required_remote_branch(
        console_env,
        local_branch,
        cfg,
    )
    remote_target = GitBranchName(f"{cfg.remote.value}/{remote_branch.value}")
    info(console_env, remote_target.value)
    git.fetch(console_env, git_env, cfg.remote)
    git.rebase(console_env, git_env, remote_target)
    branches.validate_not_remote_pr(console_env, local_branch)
    commits = repo.get_commit_stack(
        console_env,
        git_env,
        cfg.remote,
        remote_branch,
    )
    commit_stack = clean_up_deleted_commits(
        console_env,
        github_env,
        status.pull_requests,
        commits,
        cfg.root_dir,
    )
    pr_count = len(commit_stack)
    new_commits = [CommitPr(commit, None) for commit in commits[pr_count:]]
    commit_stack.extend(new_commits)
    update_patches(file_env, cfg.root_dir, commits)
    return status, commit_stack


def clean_up_deleted_commits(
    console_env: console.Env,
    github_env: github.Env,
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
                console_env,
                github_env,
                pr,
                "Closing pull request: commit has gone away",
            )
            git.delete_patch(pr.zen_token, root_dir)
        else:
            commit = zen_tokens[pr.zen_token]
            kept.append(CommitPr(commit, pr))
    return kept


def update_patches(
    file_env: file.Env,
    root_dir: GitRootDir,
    commits: List[GitCommit],
) -> None:
    for commit in commits:
        patch = GitPatch(commit.zen_token, commit.hash)
        git.write_patch(file_env, patch, root_dir)


def update_pr_branches(
    console_env: console.Env,
    git_env: git.Env,
    commit_stack: List[CommitPr],
    author: GithubUsername,
    cfg: config.Config,
    last_pr: Optional[PullRequest] = None,
) -> None:
    if len(commit_stack) == 0:
        return
    commit_pr = commit_stack[0]
    commit = commit_pr.git_commit
    pr = commit_pr.pull_request
    if pr is None:
        branch = create_pr_branch(
            git_env,
            console_env,
            last_pr,
            cfg,
            author,
            commit.zen_token,
        )
        cherry_pick_branch(console_env, git_env, commit.zen_token, branch)
        pr = PullRequest.create_template(commit, author, cfg, branch)
    else:
        update_pr_branch(console_env, git_env, pr, cfg, last_pr)
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
    git_env: git.Env,
    console_env: console.Env,
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
    git.branch_create(console_env, git_env, branch, source_branch)
    return branch


def update_pr_branch(
    console_env: console.Env,
    git_env: git.Env,
    pr: PullRequest,
    cfg: config.Config,
    last_pr: Optional[PullRequest],
) -> None:
    branch_name = branches.pr_branch(pr)
    if git.branch_exists(console_env, git_env, branch_name):
        cherry_pick_branch(console_env, git_env, pr.zen_token, branch_name)
    else:
        branch = create_pr_branch(
            git_env,
            console_env,
            last_pr,
            cfg,
            pr.author,
            pr.zen_token,
        )
        cherry_pick_branch(console_env, git_env, pr.zen_token, branch)


def cherry_pick_branch(
    console_env: console.Env,
    git_env: git.Env,
    zen_token: ZenToken,
    branch: GitBranchName,
) -> None:
    patch_ref = git.gitzen_patch_ref(zen_token)
    original_branch = repo.get_local_branch_name(console_env, git_env)
    git.switch(console_env, git_env, branch)
    git.status(console_env, git_env)
    status = git.cherry_pick(console_env, git_env, patch_ref)
    git.status(console_env, git_env)
    empty_cherry_pick_message = (
        "The previous cherry-pick is now empty, "
        + "possibly due to conflict resolution."
    )
    if empty_cherry_pick_message in status:
        git.cherry_pick_skip(console_env, git_env)
        git.status(console_env, git_env)
    for line in status:
        conflict_match = re.search(
            r"^CONFLICT \(content\): Merge conflict in (?P<filename>.*)\s*$",
            line,
        )
        if conflict_match:
            console.error(
                console_env,
                "Error: merge conflict preparing PR branch",
            )
            exit(exit_code.CONFLICT_PREPARING_PR_BRANCH)
    git.switch(console_env, git_env, original_branch)


def publish_pr_branches(
    console_env: console.Env,
    git_env: git.Env,
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
    git.push(console_env, git_env, cfg.remote, pr_branch)
    publish_pr_branches(
        console_env,
        git_env,
        commit_stack[1:],
        author,
        cfg,
        GitBranchName(commit.zen_token.value),
    )


def regenerate_prs(
    console_env: console.Env,
    github_env: github.Env,
    commit_stack: List[CommitPr],
    author: GithubUsername,
    cfg: config.Config,
    last_pr_branch: Optional[GitBranchName] = None,
) -> None:
    if len(commit_stack) == 0:
        return
    if last_pr_branch is None:
        base_branch = cfg.default_remote_branch
    else:
        base_branch = last_pr_branch
    commit_pr = commit_stack[0]
    commit = commit_pr.git_commit
    pr = commit_pr.pull_request
    if pr is None:
        pr_branch = branches.pr_branch_planned(
            author,
            base_branch,
            commit.zen_token,
        )
        create_pr(console_env, github_env, pr_branch, base_branch, commit)
    else:
        pr_branch = branches.pr_branch(pr)
        update_pr(console_env, github_env, pr_branch, base_branch, commit)
    regenerate_prs(
        console_env,
        github_env,
        commit_stack[1:],
        author,
        cfg,
        pr_branch,
    )


def create_pr(
    console_env: console.Env,
    github_env: github.Env,
    head: GitBranchName,
    base: GitBranchName,
    commit: GitCommit,
) -> None:
    github.create_pull_request(console_env, github_env, head, base, commit)


def update_pr(
    console_env: console.Env,
    github_env: github.Env,
    pr_branch: GitBranchName,
    base: GitBranchName,
    commit: GitCommit,
) -> None:
    github.update_pull_request(
        console_env,
        github_env,
        pr_branch,
        base,
        commit,
    )
