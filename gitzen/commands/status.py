from gitzen import console, envs, github
from gitzen.console import info


def status(
    console_env: console.Env,
    git_env: envs.GitEnv,
    github_env: envs.GithubEnv,
) -> None:
    info(console_env, "Querying Github...")
    prs = github.fetch_info(console_env, git_env, github_env).pull_requests
    if len(prs) == 0:
        info(console_env, "Stack is empty - no PRs found")
        exit
    for pr in prs:
        n = pr.number.value
        m = pr.mergeable.value
        t = pr.title.value
        info(console_env, f"PR-{n} - {m} - {t}")
