from typing import Dict, List

from gitzen import branches, config, envs, git, github, repo
from gitzen.console import say
from gitzen.models.git_commit import GitCommit
from gitzen.models.git_patch import GitPatch
from gitzen.models.github_pull_request import PullRequest
from gitzen.types import GitBranchName, GitRootDir, ZenToken


def push(
    console_env: envs.ConsoleEnv,
    git_env: envs.GitEnv,
    github_env: envs.GithubEnv,
    config: config.Config,
) -> None:
    status = github.fetch_info(console_env, git_env, github_env)
    local_branch = status.local_branch
    say(console_env, f"local branch: {local_branch.value}")
    remote_branch = branches.get_required_remote_branch(
        console_env, local_branch, config
    )
    remote_target = GitBranchName(
        f"remote branch: {config.remote.value}/{remote_branch.value}"
    )
    say(console_env, remote_target.value)
    git.fetch(git_env, config.remote)
    git.rebase(git_env, remote_target)
    branches.validate_not_remote_pr(console_env, local_branch)
    commits = repo.get_commit_stack(
        console_env,
        git_env,
        config.remote,
        remote_branch,
    )
    say(console_env, repr(commits))
    open_prs = clean_up_deleted_commits(
        github_env,
        status.pull_requests,
        commits,
    )
    open_prs
    # check_for_reordered_commits(git_env, open_prs, commits)
    update_patches(config.root_dir, commits)
    # sync commit stach to github
    # call git zen status


def clean_up_deleted_commits(
    github_env: envs.GithubEnv,
    pull_requests: List[PullRequest],
    commits: List[GitCommit],
) -> List[PullRequest]:
    """
    Any PR that has a zen-token that isn't in the current commit stack
    is closed as the commit has gone away.
    Issue: if commit is on another branch?
    """
    # TODO zen_map can just be a list of ZenTokens
    zen_map: Dict[ZenToken, GitCommit] = {}
    for commit in commits:
        zen_map[commit.zen_token] = commit
    kept = []
    for pr in pull_requests:
        if pr.zen_token not in zen_map:
            github.close_pull_request_with_comment(
                github_env, pr, "Closing pull request: commit has gone away"
            )
        else:
            kept.append(pr)
    return kept


def check_for_reordered_commits(
    git_env: envs.GitEnv,
    open_prs: List[PullRequest],
    commits: List[GitCommit],
) -> None:
    if reordered(open_prs, commits):
        for pr in open_prs:
            pass
            # rebase on target branch
            git.switch(git_env, pr.headRefName)
            git.rebase(git_env, pr.baseRefName)
            # get remote branch name from repo as baseRefName (default master)
            # if there was a previous commit
            # - here there never is - but generic code might
            # # get the baseRefName from that previous commit
            # format body from list of pull requests
            # title from commit
            # github.update_pull_request
            # # setting: baseRefName, title and body
        # sync commit stack to github:
        # # syncCommitStackToGitHub gets all local commits in the given branch
        # # which are new (on top of remote branch) and creates a corresponding
        # # branch on github for each commit.
        # # - git status --porcelain --untracked-files=no
        # # - if output is not blank then:
        # # # git stash
        # # # defer: git stash pop
        # update all PRs


def reordered(
    open_prs: List[PullRequest],
    commits: List[GitCommit],
) -> bool:
    for i, pr in enumerate(open_prs):
        if pr.commits[0] != commits[i]:
            return True
    return False


# # sync commit stack to github
# # loop over each local commit
#     # if it has a PR
#         # add it to a PR update queue with a note of the previous commit
#           (unless first commit)
#     # if it has no PR
#         # create as a new PR
#         # add it to a PR update queue with a note of the previous commit
#           (unless first commit)
# # loop over the PR update queue
#     # update the PR


# # call: git zen status


def update_patches(
    root_dir: GitRootDir,
    commits: List[GitCommit],
) -> List[GitPatch]:
    patches: List[GitPatch] = []
    for commit in commits:
        patch = GitPatch(commit.zen_token, commit.hash)
        git.write_patch(patch, root_dir)
        patches.append(patch)
    return patches
