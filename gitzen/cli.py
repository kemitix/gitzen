from typing import List

from gitzen import config, envs, git, github, repo
from gitzen.commands import hook, push, status
from gitzen.console import RealConsoleEnv, say


def main(args: List[str]) -> None:
    console_env: envs.ConsoleEnv = RealConsoleEnv()
    say(console_env, "`git zen` - prototype")

    git_env: envs.GitEnv = git.RealGitEnv()

    # verify that we are in a git repo or exit
    rootDir = repo.root_dir(git_env)

    github_env: envs.GithubEnv = github.RealGithubEnv()
    cfg = config.load(console_env, rootDir)

    for i, arg in enumerate(args):
        if i != 1:
            continue
        if arg == "init":
            pass  # install the commit_msg hook
        if arg == "hook":
            hook.main(args[2:])
        if arg == "status":
            status.status(console_env, git_env, github_env)
        if arg == "push":
            push.push(console_env, git_env, github_env, cfg)
