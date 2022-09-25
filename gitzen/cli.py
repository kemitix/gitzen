from typing import List, Tuple

from gitzen import config, console, file, git, github, logger
from gitzen.commands import hook, init, merge, push, status


def main(args: List[str]) -> None:
    logs: List[str] = []
    console_env, file_env, git_env, github_env = environments(logs)
    root_dir = git.root_dir(git_env)
    cfg = config.load(console_env, file_env, root_dir)
    args.pop(0)  # remove commands own name
    while len(args) > 0:
        arg = args[0]
        args.pop(0)
        if arg == "--log":
            logs.extend(args[0].split(","))
            console_env, file_env, git_env, github_env = environments(logs)
        if arg == "init":
            init.install_hook(console_env, file_env, root_dir)
            return
        if arg == "hook":
            hook.main(file_env, args[0])
            return
        if arg == "status":
            status.status(console_env, git_env, github_env)
            return
        if arg == "push":
            push.push(console_env, file_env, git_env, github_env, cfg)
            return
        if arg == "merge":
            merge.merge(console_env, file_env, git_env, github_env, cfg)
            return
    print("ERROR: no recognised command found")


def environments(
    log_sections: List[str],
) -> Tuple[console.Env, file.Env, git.Env, github.Env]:
    logger_env = logger.RealEnv(log_sections)
    return (
        console.RealEnv(log_sections),
        file.RealEnv(logger_env),
        git.RealEnv(logger_env),
        github.RealEnv(logger_env),
    )
