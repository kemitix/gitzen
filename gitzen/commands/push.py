from typing import Dict, List

from gitzen import branches, config, envs, git, github, repo
from gitzen.models.github_commit import Commit
from gitzen.models.github_pull_request import PullRequest


def push(git_github_env: envs.GitGithubEnv, config: config.Config) -> None:
    status = github.fetch_info(git_github_env)
    local_branch = status.local_branch
    print(f"local branch: {local_branch}")
    remote_branch = branches.get_required_remote_branch(local_branch, config)
    print(f"remote branch: {config.remote}/{remote_branch}")
    git.rebase(git_github_env.git_env, f"{config.remote}/{remote_branch}")
    branches.validate_not_remote_pr(local_branch)
    commit_stack = repo.get_commit_stack(
        git_github_env.git_env,
        config.remote,
        remote_branch,
    )
    print(repr(commit_stack))
    open_prs = close_prs_for_deleted_commits(
        git_github_env.github_env, status.pull_requests, commit_stack
    )
    open_prs
    # check_for_reordered_commits(github_env, status, commit_stack)
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


# # check for commits having been reordered
#     # rebase all PRs on target branch
#     # update all PRs


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
