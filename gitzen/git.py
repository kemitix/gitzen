import subprocess
import shlex
from typing import List


def _git(args: str) -> List[str]:
    result = subprocess.run(shlex.split(f'git {args}'))
    stdout = result.stdout
    if (stdout):
        lines = stdout.decode().splitlines()
        return lines
    else:
        return ""

def fetch() -> List[str]:
    return _git('fetch')

def branch() -> List[str]:
    return _git('branch --no-color')
