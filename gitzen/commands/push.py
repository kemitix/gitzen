from gitzen import branches, config, envs, git, github


def push(gitGithubEnv: envs.GitGithubEnv, config: config.Config):
    status = github.fetch_info(gitGithubEnv)
    local_branch = status.local_branch
    print(f"local branch: {local_branch}")
    remote_branch = branches.get_required_remote_branch(local_branch, config)
    git.rebase(gitGithubEnv.gitEnv, f"{config.remote}/{remote_branch}")
    branches.validate_not_remote_pr(local_branch)


# # get local commit stack: HEAD...@{upstream}
#     # get remote branch name as targetBRanch
#     # logCommand =
#  fmt.Sprintf("log --no-color %s/%s..HEAD", sd.config.Repo.GitHubRemote,
#  targetBranch)
#     # do logComment give logStack
#     # parse logStack to get commits and check if valid
#         # while parsing log stack add details to new list in reverse
#           order to that they are then read oldest first
#         # scan the git log output
#         # collect commit hash and a custom tag that we will add to
#           each commit
#         # if custom tag is missing - abort - not valid - caller should
#           rebase and add custom tags
#         # note where commit message start with 'WIP'
#         # populate fields of commit:
#         	// CommitID is a long lasting id describing the commit.
# 	        //  The CommitID is generated and added to the end of the
#               commit message on the initial commit.
#             //  The CommitID remains the same when a commit is amended.
#             CommitID string
#             // CommitHash is the git commit hash, this gets updated
#                everytime the commit is amended.
#             CommitHash string
#             // Subject is the subject of the commit message.
#             Subject string
#             // Body is the body of the commit message.
#             Body string
#             // WIP is true if the commit is still work in progress.
#             WIP bool
#     # if not valid then
#         # rebase and add custom tags
#         # do logCommand again and parse logStack
#         # if still not valid - abort - panic!
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
