import shlex
import subprocess
from typing import List


def _git(args: str) -> List[str]:
    result: subprocess.CompletedProcess[bytes] = subprocess.run(
        shlex.split(f"git {args}"), stdout=subprocess.PIPE
    )
    stdout = result.stdout
    if stdout:
        lines = stdout.decode().splitlines()
        return lines
    else:
        return ""


def fetch() -> List[str]:
    return _git("fetch")


def branch() -> List[str]:
    return _git("branch --no-color")
