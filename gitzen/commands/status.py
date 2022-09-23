from gitzen import console, git, github


def status(
    console_env: console.Env,
    git_env: git.Env,
    github_env: github.Env,
) -> None:
    prs = github.fetch_info(console_env, git_env, github_env).pull_requests
    if len(prs) == 0:
        console.info(console_env, "Stack is empty - no Pull Requests found")
        exit
    for pr in prs:
        n = pr.number.value
        m = pr.mergeable.value
        t = pr.title.value
        console.info(console_env, f"PR-{n} - {m} - {t}")
