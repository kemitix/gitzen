import os
import stat

from gitzen import console, file
from gitzen.console import info
from gitzen.types import GitRootDir


def install_hook(
    console_env: console.Env,
    file_env: file.Env,
    root_dir: GitRootDir,
) -> None:
    hook = f"{root_dir.value}/.git/hooks/commit-msg"
    file.write(
        file_env,
        hook,
        [
            "#!/usr/bin/env bash",
            "git zen hook $1",
            "",
        ],
    )
    os.chmod(hook, os.stat(hook).st_mode | stat.S_IEXEC)
    info(console_env, "Installed git zen hook")
