from typing import List

from gitzen import config, console, git, github
from gitzen.commands import hook, init, push, status
from gitzen.console import RealConsoleEnv


def main(args: List[str]) -> None:
    console_env: console.Env = RealConsoleEnv()

    git_env = git.RealGitEnv()

    # verify that we are in a git repo or exit
    root_dir = git.root_dir(console_env, git_env)

    github_env = github.RealGithubEnv()
    cfg = config.load(console_env, root_dir)

    for i, arg in enumerate(args):
        if i != 1:
            continue
        if arg == "init":
            init.install_hook(console_env, root_dir)
        if arg == "hook":
            hook.main(args[2:])
        if arg == "status":
            status.status(console_env, git_env, github_env)
        if arg == "push":
            push.push(console_env, git_env, github_env, cfg)
