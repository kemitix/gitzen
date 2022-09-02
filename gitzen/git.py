import shlex
import subprocess
from typing import List

from gitzen.envs import GitEnv


class RealGitEnv(GitEnv):
    def git(self, args: str) -> List[str]:
        result: subprocess.CompletedProcess[bytes] = subprocess.run(
            shlex.split(f"git {args}"), stdout=subprocess.PIPE
        )
        stdout = result.stdout
        if stdout:
            lines = stdout.decode().splitlines()
            return lines
        else:
            return ""


def branch(env: GitEnv) -> List[str]:
    return env.git("branch --no-color")


def fetch(env: GitEnv) -> List[str]:
    return env.git("fetch")


def remote(env: GitEnv) -> List[str]:
    return env.git("remote --verbose")


def revParse(env: GitEnv, args: str = "") -> List[str]:
    return env.git(f"rev-parse {args}")
