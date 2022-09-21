from typing import List

from gitzen import config, console, file, git, github
from gitzen.commands import hook, init, push, status


def main(args: List[str]) -> None:
    console_env = console.RealEnv()
    git_env = git.RealEnv()
    # verify that we are in a git repo or exit
    root_dir = git.root_dir(console_env, git_env)
    file_env = file.RealEnv()
    cfg = config.load(console_env, file_env, root_dir)
    github_env = github.RealEnv()
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
