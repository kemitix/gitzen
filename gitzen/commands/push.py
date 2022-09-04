from gitzen import branches, config, envs, git, github, repo


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
    commit_stack


# # close prs for delete commits
#     # create a map of local commits by the tag we added to them
#     # loop over each PR looking for the commit tag in each
#     # if there is no local commit in the stack - comment and close the PR
#         # what if the commit is on another stack?
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
