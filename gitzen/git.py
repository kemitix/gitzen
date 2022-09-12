import shlex
import subprocess
from typing import List

from gitzen.envs import GitEnv
from gitzen.types import GitBranchName, GitRemoteName


class RealGitEnv(GitEnv):
    def git(self, args: str) -> List[str]:
        git_command = f"git {args}"
        result: subprocess.CompletedProcess[bytes] = subprocess.run(
            shlex.split(git_command), stdout=subprocess.PIPE
        )
        stdout = result.stdout
        if stdout:
            lines = stdout.decode().splitlines()
            return lines
        else:
            return []


def branch(env: GitEnv) -> List[str]:
    return env.git("branch --no-color")


def fetch(env: GitEnv, remote: GitRemoteName) -> List[str]:
    return env.git(f"fetch {remote.value}")


def log(env: GitEnv, args: str = "") -> List[str]:
    return env.git(f"log --no-color {args}")


def rebase(env: GitEnv, target: GitBranchName) -> List[str]:
    return env.git(f"rebase {target.value} --autostash")


def remote(env: GitEnv) -> List[str]:
    return env.git("remote --verbose")


def rev_parse(env: GitEnv, args: str = "") -> List[str]:
    return env.git(f"rev-parse {args}")


def switch(env: GitEnv, branch: GitBranchName) -> List[str]:
    return env.git(f"switch {branch.value}")
