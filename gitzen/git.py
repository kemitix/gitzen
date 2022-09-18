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
        print(f"{git_command} >")
        result: subprocess.CompletedProcess[bytes] = subprocess.run(
            shlex.split(git_command),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        stdout = result.stdout
        if stdout:
            lines = stdout.decode().splitlines()
            [print(f"| {line}") for line in lines]
            print("\\------------------")
            return lines
        else:
            print("\\------------------")
            return []


def gitzen_refs(root_dir: GitRootDir) -> str:
    return f"{root_dir.value}/.git/refs/gitzen"


def gitzen_patches(root_dir: GitRootDir) -> str:
    return f"{gitzen_refs(root_dir)}/patches"


def gitzen_patch_file(zen_token: ZenToken, root_dir: GitRootDir) -> str:
    return f"{gitzen_patches(root_dir)}/{zen_token.value}"


def gitzen_patch_ref(zen_token: ZenToken) -> GitBranchName:
    return GitBranchName(f"gitzen/patches/{zen_token.value}")


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


def cherry_pick_continue(env: GitEnv) -> List[str]:
    return env.git("cherry-pick --continue")


def fetch(env: GitEnv, remote: GitRemoteName) -> List[str]:
    return env.git(f"fetch {remote.value}")


def init(env: GitEnv) -> List[str]:
    return env.git("init")


def init_bare(env: GitEnv) -> List[str]:
    return env.git("init --bare")


def clone(env: GitEnv, remote_repo: str, local_dir: str) -> List[str]:
    return env.git(f"clone {remote_repo} {local_dir}")


def add(env: GitEnv, files: List[str]) -> List[str]:
    return env.git(f"add {' '.join(files)}")


def commit(env: GitEnv, message: List[str]) -> List[str]:
    log = "\n".join(message)
    return env.git(f"commit -m'{log}'")


def commit_amend_noedit(env: GitEnv) -> List[str]:
    return env.git("commit --amend --no-edit")


def log(env: GitEnv, args: str = "") -> List[str]:
    return env.git(f"log --no-color {args}")


def status(env: GitEnv) -> List[str]:
    return env.git("status")


def push(
    git_env: GitEnv,
    remote: GitRemoteName,
    branch: GitBranchName,
) -> List[str]:
    return git_env.git(f"push {remote.value} {branch.value}:{branch.value}")


def rebase(env: GitEnv, target: GitBranchName) -> List[str]:
    return env.git(f"rebase {target.value} --autostash")


def remote(env: GitEnv) -> List[str]:
    return env.git("remote --verbose")


def remote_add(
    env: GitEnv,
    remote_name: GitRemoteName,
    root_dir: GitRootDir,
) -> List[str]:
    return env.git(f"remote add {remote_name.value} {root_dir.value}")


def rev_parse(env: GitEnv, args: str = "") -> List[str]:
    return env.git(f"rev-parse {args}")


def switch(env: GitEnv, branch: GitBranchName) -> List[str]:
    return env.git(f"switch {branch.value}")


def log_graph(env: GitEnv) -> List[str]:
    return env.git("log --oneline --graph --decorate --all")
