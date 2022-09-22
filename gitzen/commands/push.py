import re
from typing import Dict, List, Optional, Tuple

# trunk-ignore(flake8/E501)
from gitzen import branches, config, console, exit_code, file, git, github, repo
from gitzen.config import Config
from gitzen.models.commit_branches import CommitBranches
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
) -> Tuple[GithubInfo, List[CommitBranches]]:
    print("::: push.prepare_pr_branches")
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
    )
    return status, commit_stack


def prepare_patches(
    console_env: console.Env,
    file_env: file.Env,
    git_env: git.Env,
    github_env: github.Env,
    cfg: Config,
) -> Tuple[GithubInfo, List[CommitBranches]]:
    print("::: prepare_patches")
    status = github.fetch_info(console_env, git_env, github_env)
    local_branch = status.local_branch
    remote_branch = branches.get_required_remote_branch(
        console_env,
        local_branch,
        cfg,
    )
    remote_target = GitBranchName(f"{cfg.remote.value}/{remote_branch.value}")
    git.fetch(git_env, cfg.remote)
    git.rebase(git_env, remote_target)
    branches.validate_not_remote_pr(console_env, local_branch)
    commits = repo.get_commit_stack(
        console_env,
        git_env,
        cfg.remote,
        remote_branch,
    )
    update_patches(console_env, file_env, cfg.root_dir, commits)
    commit_stack = clean_up_deleted_commits(
        github_env,
        status.pull_requests,
        commits,
        cfg.root_dir,
    )
    pr_count = len(commit_stack)
    new_commits = [CommitPr(commit, None) for commit in commits[pr_count:]]
    commit_stack.extend(new_commits)
    return status, rethread_stack(
        status.username,
        commit_stack,
        remote_branch,
        remote_target=remote_target,
    )


def rethread_stack(
    author: GithubUsername,
    commit_stack: List[CommitPr],
    prev_head: GitBranchName,
    prev_token: Optional[ZenToken] = None,
    remote_target: Optional[GitBranchName] = None,
) -> List[CommitBranches]:
    if len(commit_stack) == 0:
        return []
    hd = commit_stack[0]
    if remote_target is not None:
        head = branches.pr_branch_planned(
            author,
            prev_head,
            hd.git_commit.zen_token,
        )
    else:
        if prev_token is None:
            head = branches.pr_branch_planned(
                author, prev_head, hd.git_commit.zen_token
            )
        else:
            head = branches.pr_branch_planned(
                author,
                GitBranchName(prev_token.value),
                hd.git_commit.zen_token,
            )
    result: List[CommitBranches] = [
        CommitBranches(
            hd.git_commit,
            prev_head,
            head,
            hd.pull_request,
            remote_target,
        ),
    ]
    result.extend(
        rethread_stack(
            author, commit_stack[1:], head, prev_token=hd.git_commit.zen_token
        )
    )
    return result


def clean_up_deleted_commits(
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
    console_env: console.Env,
    file_env: file.Env,
    root_dir: GitRootDir,
    commits: List[GitCommit],
) -> None:
    for commit in commits:
        patch = GitPatch(commit.zen_token, commit.hash)
        git.write_patch(file_env, patch, root_dir)
        console.info(console_env, f"Wrote patch: {patch.zen_token.value}")


def update_pr_branches(
    console_env: console.Env,
    git_env: git.Env,
    commit_stack: List[CommitBranches],
) -> None:
    if len(commit_stack) == 0:
        return
    print(f"::: push.update_pr_branches: {len(commit_stack)}")
    update_pr_branch(console_env, git_env, commit_stack[0])
    update_pr_branches(
        console_env,
        git_env,
        commit_stack[1:],
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


def update_pr_branch(
    console_env: console.Env,
    git_env: git.Env,
    commit_branches: CommitBranches,
) -> None:
    head = commit_branches.head
    base = commit_branches.base
    print(f"::: push.update_pr_branch: {base} <- {head}")
    if not git.branch_exists(git_env, head):
        if commit_branches.remote_target is not None:
            git.branch_create(git_env, head, commit_branches.remote_target)
        else:
            git.branch_create(git_env, head, base)
    zen_token = commit_branches.git_commit.zen_token
    cherry_pick_branch(console_env, git_env, zen_token, head)


def cherry_pick_branch(
    console_env: console.Env,
    git_env: git.Env,
    zen_token: ZenToken,
    branch: GitBranchName,
) -> None:
    patch_ref = git.gitzen_patch_ref(zen_token)
    original_branch = repo.get_local_branch_name(console_env, git_env)
    print(f"::: push.cherry_pick_branch: {branch} <- {patch_ref}")
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
            console.error(
                console_env,
                "Error: merge conflict preparing PR branch",
            )
            exit(exit_code.CONFLICT_PREPARING_PR_BRANCH)
    git.switch(git_env, original_branch)
    git.log_graph(git_env)


def publish_pr_branches(
    console_env: console.Env,
    git_env: git.Env,
    commit_stack: List[CommitBranches],
    author: GithubUsername,
    cfg: config.Config,
) -> None:
    if len(commit_stack) == 0:
        return
    pr_branch = commit_stack[0].head
    print(f"::: push.publish_pr_branches: {pr_branch}")
    git.push(git_env, cfg.remote, pr_branch)
    publish_pr_branches(
        console_env,
        git_env,
        commit_stack[1:],
        author,
        cfg,
    )


def regenerate_prs(
    console_env: console.Env,
    github_env: github.Env,
    commit_stack: List[CommitBranches],
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
    commit_branches = commit_stack[0]
    commit = commit_branches.git_commit
    pr = commit_branches.pull_request
    pr_branch = commit_branches.head
    print(f"::: push.regenerate_prs: {base_branch} <- {pr_branch}")
    if pr is None:
        github.create_pull_request(github_env, pr_branch, base_branch, commit)
    else:
        github.update_pull_request(github_env, pr_branch, base_branch, commit)
    regenerate_prs(
        console_env,
        github_env,
        commit_stack[1:],
        author,
        cfg,
        pr_branch,
    )
