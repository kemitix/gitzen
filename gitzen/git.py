import shlex
import subprocess
from typing import List


class GitEnv:
    def git(self, args: str) -> List[str]:
        pass


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


def revParse(env: GitEnv, args: str = "") -> List[str]:
    return env.git(f"rev-parse {args}")


def fetch(env: GitEnv) -> List[str]:
    return env.git("fetch")


def branch(env: GitEnv) -> List[str]:
    return env.git("branch --no-color")


def remote(env: GitEnv) -> List[str]:
    return env.git("remote --verbose")
