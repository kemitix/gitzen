import subprocess
import shlex
from typing import List


class Git:
    def _git(args: str) -> List[str]:
        result = subprocess.run(shlex.split(f'git {args}'))
        stdout = result.stdout
        if (stdout):
            lines = stdout.decode().splitlines()
            return lines
        else:
            return ""

    def fetch() -> List[str]:
        return Git._git('fetch')
