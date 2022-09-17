from gitzen import envs, file
from gitzen.console import say
from gitzen.types import GitRootDir


def install_hook(console_env: envs.ConsoleEnv, root_dir: GitRootDir) -> None:
    file.write(
        f"{root_dir.value}/.git/hooks/commit-msg",
        [
            "#!/usr/bin/env bash",
            "git zen hook $1",
            "",
        ],
    )
    say(console_env, "Installed git zen hook")
