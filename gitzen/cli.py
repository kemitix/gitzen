from typing import List, Tuple

from gitzen import config, console, file, git, github, logger
from gitzen.commands import hook, init, push, status


def main(args: List[str]) -> None:
    logs: List[str] = []
    args.pop(0)  # remove commands own name
    while len(args) > 0:
        arg = args[0]
        args.pop(0)
        if arg == "--log":
            logs.extend(args[0].split(","))
        if arg == "init":
            (console_env, file_env, git_env, _) = environments(logs)
            root_dir = git.root_dir(git_env)
            init.install_hook(console_env, file_env, root_dir)
        if arg == "hook":
            (_, file_env, _, _) = environments(logs)
            hook.main(file_env, args[0])
        if arg == "status":
            (console_env, _, git_env, github_env) = environments(logs)
            status.status(console_env, git_env, github_env)
        if arg == "push":
            (console_env, file_env, git_env, github_env) = environments(logs)
            root_dir = git.root_dir(git_env)
            cfg = config.load(console_env, file_env, root_dir)
            push.push(console_env, file_env, git_env, github_env, cfg)


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
