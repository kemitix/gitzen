from typing import Dict, List

from gitzen import branches, config, envs, git, github, repo
from gitzen.models.github_commit import Commit
from gitzen.models.github_pull_request import PullRequest


def push(git_github_env: envs.GitGithubEnv, config: config.Config) -> None:
    git_env = git_github_env.git_env
    github_env = git_github_env.github_env
    status = github.fetch_info(git_github_env)
    local_branch = status.local_branch
    print(f"local branch: {local_branch}")
    remote_branch = branches.get_required_remote_branch(local_branch, config)
    print(f"remote branch: {config.remote}/{remote_branch}")
    git.rebase(git_env, f"{config.remote}/{remote_branch}")
    branches.validate_not_remote_pr(local_branch)
    commits = repo.get_commit_stack(git_env, config.remote, remote_branch)
    print(repr(commits))
    open_prs = close_prs_for_deleted_commits(github_env, status.pull_requests, commits)
    check_for_reordered_commits(github_env, open_prs, commits)
    # sync commit stach to github
    # call git zen status


def close_prs_for_deleted_commits(
    github_env: envs.GithubEnv,
    pull_requests: List[PullRequest],
    commits: List[Commit],
) -> List[PullRequest]:
    zen_map: Dict[str, Commit] = {}
    for commit in commits:
        if commit.zen_token is not None:
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
    github_env: envs.GithubEnv,
    open_prs: List[PullRequest],
    commits: List[Commit],
) -> None:
    if reordered(open_prs, commits):
        for pr in open_prs:
            pass
            # rebase on target branch
            # get remote branch name from repo as baseRefName (default master)
            # if there was a previous commit - here there never is - generic code might
            # # get the baseRefName from that previous commit
            # format body from list of pull requests
            # title from commit
            # github.update_pull_request
            # # setting: baseRefName, title and body
        # sync commit stack to github:
        # # syncCommitStackToGitHub gets all the local commits in the given branch
        # # which are new (on top of remote branch) and creates a corresponding
        # # branch on github for each commit.
        # # - git status --porcelain --untracked-files=no
        # # - if output is not blank then:
        # # # git stash
        # # # defer: git stash pop
        # update all PRs


def reordered(open_prs: List[PullRequest], commits: List[Commit]) -> bool:
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
