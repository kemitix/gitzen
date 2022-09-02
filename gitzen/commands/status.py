from gitzen import github
from gitzen.envs import GitGithubEnv


def status(gitGithubEnv: GitGithubEnv):
    print("Querying Github...")
    prs = github.fetchInfo(gitGithubEnv).pull_requests
    numPRs = len(prs)
    if numPRs == 0:
        print("Stack is empty - no PRs found")
        exit
    for pr in prs:
        n = pr.number
        m = pr.mergeable
        t = pr.title
        print(f"PR-{n} - {m} - {t}")
