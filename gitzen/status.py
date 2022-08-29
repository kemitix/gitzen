from gitzen import github


def status(env: github.Env):
    print("Querying Github...")
    prs = github.pullRequests(env)
    numPRs = len(prs)
    if numPRs == 0:
        print("Stack is empty - no PRs found")
        exit
    for pr in prs:
        n = pr.number
        m = pr.mergeable
        t = pr.title
        print(f"PR-{n} - {m} - {t}")
