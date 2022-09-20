from typing import List

from gitzen import config, console, file, git, github
from gitzen.commands import hook, init, push, status
from gitzen.console import RealConsoleEnv


def main(args: List[str]) -> None:
    console_env: console.Env = RealConsoleEnv()
    git_env = git.RealGitEnv()
    # verify that we are in a git repo or exit
    root_dir = git.root_dir(console_env, git_env)
    file_env = file.RealEnv()
    cfg = config.load(console_env, file_env, root_dir)
    github_env = github.RealGithubEnv()
    file_env = file.RealEnv()
    arg = args[1]
    if arg == "init":
        init.install_hook(console_env, file_env, root_dir)
    if arg == "hook":
        hook.main(file_env, args[2:])
    if arg == "status":
        status.status(console_env, git_env, github_env)
    if arg == "push":
        push.push(console_env, file_env, git_env, github_env, cfg)
