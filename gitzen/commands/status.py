from gitzen import envs, github
from gitzen.console import say


def status(
    console_env: envs.ConsoleEnv,
    git_env: envs.GitEnv,
    github_env: envs.GithubEnv,
) -> None:
    say(console_env, "Querying Github...")
    prs = github.fetch_info(console_env, git_env, github_env).pull_requests
    numPRs = len(prs)
    if numPRs == 0:
        say(console_env, "Stack is empty - no PRs found")
        exit
    for pr in prs:
        n = pr.number
        m = pr.mergeable
        t = pr.title
        say(console_env, f"PR-{n} - {m} - {t}")
