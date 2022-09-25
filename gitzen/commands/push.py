import re
from typing import Dict, List, Optional, Tuple

# trunk-ignore(flake8/E501)
from gitzen import branches, config, console, exit_code, file, git, github, logger, repo
from gitzen.config import Config
from gitzen.models.commit_branches import CommitBranches
from gitzen.models.commit_pr import CommitPr
from gitzen.models.git_commit import GitCommit
from gitzen.models.git_patch import GitPatch
from gitzen.models.github_info import GithubInfo
from gitzen.models.github_pull_request import PullRequest
from gitzen.models.gitzen_error import GitZenError

# trunk-ignore(flake8/E501)
from gitzen.types import CommitHash, GitBranchName, GithubUsername, GitRootDir, ZenToken


def push(
    console_env: console.Env,
    file_env: file.Env,
    git_env: git.Env,
    github_env: github.Env,
    cfg: config.Config,
) -> None:
    initial_branch = repo.get_local_branch_name(console_env, git_env)
    try:
        if initial_branch != cfg.default_remote_branch:
            raise GitZenError(
                exit_code.UNSUPPORTED_BRANCH_FOR_PUSH,
                "git zen currently only supports working "
                "from the default branch "
                f"(i.e. '{cfg.default_remote_branch.value}')",
            )
        status, commit_stack, pr_head_hashes = prepare_pr_branches(
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
            pr_head_hashes,
            cfg,
        )
        regenerate_prs(
            console_env,
            github_env,
            commit_stack,
            pr_head_hashes,
            status.username,
            cfg,
        )
    except GitZenError as error:
        console.error(console_env, error.message)
        exit(error.exit_code)
    finally:
        git.switch(git_env, initial_branch)


def prepare_pr_branches(
    console_env: console.Env,
    file_env: file.Env,
    git_env: git.Env,
    github_env: github.Env,
    cfg: Config,
) -> Tuple[GithubInfo, List[CommitBranches], List[CommitHash]]:
    status, commit_stack = prepare_patches(
        console_env,
        file_env,
        git_env,
        github_env,
        cfg,
    )
    pr_head_hashes = update_pr_branches(
        console_env,
        git_env,
        commit_stack,
    )
    git.switch(git_env, cfg.default_remote_branch)
    return status, commit_stack, pr_head_hashes


def prepare_patches(
    console_env: console.Env,
    file_env: file.Env,
    git_env: git.Env,
    github_env: github.Env,
    cfg: Config,
) -> Tuple[GithubInfo, List[CommitBranches]]:
    console.info(console_env, "Preparing patches")
    status = github.fetch_info(console_env, git_env, github_env)
    local_branch = status.local_branch
    branches.validate_not_remote_pr(console_env, local_branch)
    remote_branch = branches.get_required_remote_branch(
        console_env,
        local_branch,
        cfg,
    )
    remote_target = GitBranchName(f"{cfg.remote.value}/{remote_branch.value}")
    git.fetch(git_env, cfg.remote)
    git.rebase(git_env, remote_target)
    commits = repo.get_commit_stack(
        console_env,
        git_env,
        cfg.remote,
        remote_branch,
    )
    update_patches(console_env, file_env, cfg.root_dir, commits)
    commit_stack = clean_up_deleted_commits(
        console_env,
        git_env,
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
    console_env: console.Env,
    git_env: git.Env,
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
            console.warn(
                console_env,
                f"No commit for Pull Request {pr.number} closing: {pr.title}",
            )
            github.close_pull_request_with_comment(
                github_env,
                pr,
                "Closing pull request: commit has gone away",
            )
            git.delete_patch(git_env, pr.headRefName)
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
        if git.outdated_patch(file_env, patch, root_dir):
            git.write_patch(file_env, patch, root_dir)
            console.info(
                console_env,
                (
                    f"Updating patch {patch.zen_token.value}"
                    f" - {commit.messageHeadline.value}"
                ),
            )


def update_pr_branches(
    console_env: console.Env,
    git_env: git.Env,
    commit_stack: List[CommitBranches],
) -> List[CommitHash]:
    if len(commit_stack) == 0:
        return []
    hashes: List[CommitHash] = []
    hashes.append(update_pr_branch(console_env, git_env, commit_stack[0]))
    hashes.extend(
        update_pr_branches(
            console_env,
            git_env,
            commit_stack[1:],
        )
    )
    return hashes


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
) -> CommitHash:
    """
    Returns the hash of the updated pr branch.
    """
    if commit_branches.remote_target is None:
        base = commit_branches.base
    else:
        base = commit_branches.remote_target
    head = commit_branches.head
    zen_token = commit_branches.git_commit.zen_token
    if not git.branch_exists(git_env, head):
        git.branch_create(git_env, head, base)
        cherry_pick_branch(console_env, git_env, zen_token, head)
        hash = CommitHash(git.rev_parse(git_env, "HEAD")[0])
    else:
        git.switch(git_env, head)
        git.status(git_env)
        git.log_graph(git_env)
        git.rebase(git_env, base)
        commit = commit_branches.git_commit
        git.restore_staged_worktree(
            git_env,
            GitBranchName(commit.hash.value),
        )
        log = git.status(git_env)
        if not logger.line_contains(
            "nothing to commit, working tree clean",
            log,
        ):
            git.commit(
                git_env,
                [
                    f"{commit.messageHeadline.value}",
                    "",
                    f"{commit.messageBody.value}",
                    f"(updated from commit {commit.hash.value})",
                ],
            )
        hash = CommitHash(git.rev_parse(git_env, "HEAD")[0])
        git.status(git_env)
        git.log_graph(git_env)
    return hash


def cherry_pick_branch(
    console_env: console.Env,
    git_env: git.Env,
    zen_token: ZenToken,
    branch: GitBranchName,
) -> None:
    original_branch = repo.get_local_branch_name(console_env, git_env)
    patch_ref = git.gitzen_patch_ref(zen_token)
    git.switch(git_env, branch)
    status = git.cherry_pick(git_env, patch_ref)
    git.status(git_env)
    empty_cherry_pick_message = (
        "The previous cherry-pick is now empty, "
        + "possibly due to conflict resolution."
    )
    if empty_cherry_pick_message in status:
        git.cherry_pick_skip(git_env)
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


def publish_pr_branches(
    console_env: console.Env,
    git_env: git.Env,
    commit_stack: List[CommitBranches],
    pr_head_hashes: List[CommitHash],
    cfg: config.Config,
    parent_pr_branch_updated: bool = False,
) -> None:
    if len(commit_stack) == 0:
        return
    cb = commit_stack[0]
    pr_branch = cb.head
    existing_pr = cb.pull_request
    if not existing_pr or existing_pr.headHash != pr_head_hashes[0]:
        console.info(
            console_env,
            f"Updating remote branch: {cfg.remote.value}/{pr_branch.value}",
        )
        if parent_pr_branch_updated:
            git.push_force_with_lease(git_env, cfg.remote, pr_branch)
        else:
            git.push(git_env, cfg.remote, pr_branch)
        parent_pr_branch_updated = True
    publish_pr_branches(
        console_env,
        git_env,
        commit_stack[1:],
        pr_head_hashes[1:],
        cfg,
        parent_pr_branch_updated,
    )


def regenerate_prs(
    console_env: console.Env,
    github_env: github.Env,
    commit_stack: List[CommitBranches],
    pr_head_hashes: List[CommitHash],
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
    if pr is None:
        console.info(
            console_env,
            f"Creating Pull Request: {base_branch.value} <- {pr_branch.value}",
        )
        github.create_pull_request(github_env, pr_branch, base_branch, commit)
    else:
        pr_branch = commit_branches.head
        existing_pr = commit_branches.pull_request
        if not existing_pr or existing_pr.headHash != pr_head_hashes[0]:
            console.info(
                console_env,
                (
                    f"Updating Pull Request {pr.number.value}"
                    f": {base_branch.value}"
                    f" <- {pr_branch.value}"
                ),
            )
            github.update_pull_request(
                github_env,
                pr_branch,
                base_branch,
                commit,
            )
    regenerate_prs(
        console_env,
        github_env,
        commit_stack[1:],
        pr_head_hashes[1:],
        author,
        cfg,
        pr_branch,
    )
