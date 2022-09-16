import os
import shlex
import subprocess
from os import mkdir
from os.path import isdir
from typing import List

from genericpath import exists

from gitzen import exit_code, file
from gitzen.envs import GitEnv
from gitzen.models.git_patch import GitPatch
from gitzen.types import GitBranchName, GitRemoteName, GitRootDir, ZenToken


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


def gitzen_refs(root_dir: GitRootDir) -> str:
    return f"{root_dir.value}/.git/refs/gitzen"


def gitzen_patches(root_dir: GitRootDir) -> str:
    return f"{gitzen_refs(root_dir)}/patches"


def gitzen_patch_file(zen_token: ZenToken, root_dir: GitRootDir) -> str:
    return f"{gitzen_patches(root_dir)}/{zen_token.value}"


# will exit the program if called from outside a git repo
def root_dir(git_env: GitEnv) -> GitRootDir:
    output = rev_parse(git_env, "--show-toplevel")
    if output == "":
        exit(exit_code.NOT_IN_GIT_REPO)
    return GitRootDir(output[0])


def write_patch(patch: GitPatch, root_dir: GitRootDir) -> None:
    patches_dir = gitzen_patches(root_dir)
    if not isdir(patches_dir):
        mkdir(gitzen_refs(root_dir))
        mkdir(patches_dir)
    file.write(
        gitzen_patch_file(patch.zen_token, root_dir),
        [patch.hash.value],
    )


def delete_patch(zen_token: ZenToken, root_dir: GitRootDir) -> None:
    patch_file = gitzen_patch_file(zen_token, root_dir)
    if exists(patch_file):
        os.remove(patch_file)


def branch(env: GitEnv) -> List[str]:
    return env.git("branch --no-color")


def branch_create(
    env: GitEnv,
    new_branch_name: GitBranchName,
    source_branch_name: GitBranchName,
) -> List[str]:
    return env.git(
        f"branch {new_branch_name.value} {source_branch_name.value}",
    )


def branch_exists(
    env: GitEnv,
    branch_name: GitBranchName,
) -> bool:
    lines = [line[2:] for line in branch(env)]
    branches = [GitBranchName(name) for name in lines]
    return branch_name in branches


def cherry_pick(env: GitEnv, ref: GitBranchName) -> List[str]:
    return env.git(f"cherry-pick -x {ref.value}")


def cherry_pick_skip(env: GitEnv) -> List[str]:
    return env.git("cherry-pick --skip")


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
