import shlex
from pathlib import PosixPath
from subprocess import DEVNULL, run
from typing import List


def given_repo(dir: PosixPath) -> None:
    cmd = shlex.split("git init")
    run(cmd, cwd=dir, stdout=DEVNULL, stderr=DEVNULL)


def given_file(file: str, lines: List[str]) -> None:
    with open(file, "w") as fp:
        contents = "\n".join(lines)
        fp.write(contents)
