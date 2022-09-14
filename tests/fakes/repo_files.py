import shlex
from os import chdir
from subprocess import DEVNULL, run
from typing import List

from gitzen.types import GitRootDir


def given_repo(dir: GitRootDir) -> None:
    cmd = shlex.split("git init")
    run(cmd, cwd=dir.value, stdout=DEVNULL, stderr=DEVNULL)
    chdir(dir.value)


def given_file(file: str, lines: List[str]) -> None:
    with open(file, "w") as fp:
        contents = "\n".join(lines)
        fp.write(contents)
