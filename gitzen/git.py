import os
import shlex
import subprocess
from os import mkdir
from os.path import isdir
from typing import List

from genericpath import exists

from gitzen import console, exit_code, file
from gitzen.models.git_patch import GitPatch
from gitzen.types import GitBranchName, GitRemoteName, GitRootDir, ZenToken


class Env:
    def _git(
        self,
        console_env: console.Env,
        args: str,
    ) -> List[str]:
        pass

    def write_patch(self, patch: GitPatch) -> None:
        pass


class RealGitEnv(Env):
    def _git(self, console_env: console.Env, args: str) -> List[str]:
        git_command = f"git {args}"
        console.log(console_env, "git", f"{git_command}")
        result: subprocess.CompletedProcess[bytes] = subprocess.run(
            shlex.split(git_command),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        stdout = result.stdout
        if stdout:
            lines = stdout.decode().splitlines()
            [console.log(console_env, "git", f"| {line}") for line in lines]
            console.log(console_env, "git", "\\------------------")
            return lines
        else:
            console.log(console_env, "git", "\\------------------")
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
def root_dir(
    console_env: console.Env,
    git_env: Env,
) -> GitRootDir:
    output = rev_parse(console_env, git_env, "--show-toplevel")
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


def branch(
    console_env: console.Env,
    git_env: Env,
) -> List[str]:
    return git_env._git(console_env, "branch --no-color")


def branch_create(
    console_env: console.Env,
    git_env: Env,
    new_branch_name: GitBranchName,
    source_branch_name: GitBranchName,
) -> List[str]:
    return git_env._git(
        console_env,
        f"branch {new_branch_name.value} {source_branch_name.value}",
    )


def branch_exists(
    console_env: console.Env,
    git_env: Env,
    branch_name: GitBranchName,
) -> bool:
    lines = [line[2:] for line in branch(console_env, git_env)]
    branches = [GitBranchName(name) for name in lines]
    return branch_name in branches


def cherry_pick(
    console_env: console.Env,
    git_env: Env,
    ref: GitBranchName,
) -> List[str]:
    return git_env._git(console_env, f"cherry-pick -x {ref.value}")


def cherry_pick_skip(
    console_env: console.Env,
    git_env: Env,
) -> List[str]:
    return git_env._git(console_env, "cherry-pick --skip")


def cherry_pick_continue(
    console_env: console.Env,
    git_env: Env,
) -> List[str]:
    return git_env._git(console_env, "cherry-pick --continue")


def config_set(
    console_env: console.Env,
    git_env: Env,
    key: str,
    value: str,
) -> List[str]:
    return git_env._git(console_env, f"config {key} '{value}'")


def fetch(
    console_env: console.Env,
    git_env: Env,
    remote: GitRemoteName,
) -> List[str]:
    return git_env._git(console_env, f"fetch {remote.value}")


def init(
    console_env: console.Env,
    git_env: Env,
) -> List[str]:
    return git_env._git(console_env, "init")


def init_bare(
    console_env: console.Env,
    git_env: Env,
) -> List[str]:
    return git_env._git(console_env, "init --bare")


def clone(
    console_env: console.Env,
    git_env: Env,
    remote_repo: str,
    local_dir: str,
) -> List[str]:
    return git_env._git(console_env, f"clone {remote_repo} {local_dir}")


def add(
    console_env: console.Env,
    git_env: Env,
    files: List[str],
) -> List[str]:
    return git_env._git(console_env, f"add {' '.join(files)}")


def commit(
    console_env: console.Env,
    git_env: Env,
    message: List[str],
) -> List[str]:
    log = "\n".join(message)
    return git_env._git(console_env, f"commit -m'{log}'")


def commit_amend_noedit(
    console_env: console.Env,
    git_env: Env,
) -> List[str]:
    return git_env._git(console_env, "commit --amend --no-edit")


def log(
    console_env: console.Env,
    git_env: Env,
    args: str = "",
) -> List[str]:
    return git_env._git(console_env, f"log --no-color {args}")


def status(
    console_env: console.Env,
    git_env: Env,
) -> List[str]:
    return git_env._git(console_env, "status")


def push(
    console_env: console.Env,
    git_env: Env,
    remote: GitRemoteName,
    branch: GitBranchName,
) -> List[str]:
    return git_env._git(
        console_env, f"push {remote.value} {branch.value}:{branch.value}"
    )


def rebase(
    console_env: console.Env,
    git_env: Env,
    target: GitBranchName,
) -> List[str]:
    return git_env._git(console_env, f"rebase {target.value} --autostash")


def remote(
    console_env: console.Env,
    git_env: Env,
) -> List[str]:
    return git_env._git(console_env, "remote --verbose")


def remote_add(
    console_env: console.Env,
    git_env: Env,
    remote_name: GitRemoteName,
    root_dir: GitRootDir,
) -> List[str]:
    return git_env._git(
        console_env,
        f"remote add {remote_name.value} {root_dir.value}",
    )


def rev_parse(
    console_env: console.Env,
    git_env: Env,
    args: str = "",
) -> List[str]:
    return git_env._git(console_env, f"rev-parse {args}")


def switch(
    console_env: console.Env,
    git_env: Env,
    branch: GitBranchName,
) -> List[str]:
    return git_env._git(console_env, f"switch {branch.value}")


def log_graph(
    console_env: console.Env,
    git_env: Env,
) -> List[str]:
    return git_env._git(console_env, "log --oneline --graph --decorate --all")
