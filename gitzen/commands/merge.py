from gitzen import config, console, exit_code, file, git, github, logger
from gitzen.commands.push import prepare_patches, push


def merge(
    console_env: console.Env,
    file_env: file.Env,
    git_env: git.Env,
    github_env: github.Env,
    cfg: config.Config,
) -> None:
    status, stack = prepare_patches(
        console_env,
        file_env,
        git_env,
        github_env,
        cfg,
    )
    my_pr = stack[0].pull_request
    if my_pr:
        gh_pr = status.pull_requests[0]
        if my_pr.headHash == gh_pr.headHash:
            console.info(
                console_env,
                f"Merge Pull Request {gh_pr.number.value} {gh_pr.title.value}",
            )
            github.merge_squash(github_env, gh_pr)
            git.branch_delete(git_env, my_pr.headRefName)
            remote_branch = cfg.default_remote_branch
            git.switch(git_env, remote_branch)
            pull_log = git.pull(git_env, cfg.remote, remote_branch)
            if logger.line_contains("! [rejected]", pull_log):
                console.error(
                    console_env,
                    (
                        "Can't pull from "
                        f"{cfg.remote.value}/{remote_branch.value}. "
                        "The change was rejected. "
                        f"Manually update {remote_branch.value} "
                        f"with {cfg.remote.value}."
                    ),
                )
                exit(exit_code.PULL_REJECTED)
            push(console_env, file_env, git_env, github_env, cfg)
        else:
            my_commit = stack[0].git_commit
            console.warn(
                console_env,
                (
                    "The local commit doesn't match the remote PR. "
                    "Run 'git zen push' to update the PR.\n"
                    f" - local commit: {my_commit.short_hash} "
                    f"{my_commit.messageHeadline}\n"
                    f" - pull request: {my_pr.short_head_hash} "
                    f"{my_pr.title}"
                ),
            )
            exit(exit_code.LOCAL_COMMIT_REMOTE_PR_DIFFERENT_HASH)
    else:
        console.info(console_env, "No Pull Requests to be merged.")
