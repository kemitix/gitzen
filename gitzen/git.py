import os
import shlex
import subprocess
from os import mkdir
from os.path import isdir
from typing import List

from genericpath import exists

from gitzen import exit_code, file, logger
from gitzen.models.git_patch import GitPatch
from gitzen.types import GitBranchName, GitRemoteName, GitRootDir, ZenToken


class Env:
    def _git(self, args: str) -> List[str]:
        pass

    def write_patch(self, patch: GitPatch) -> None:
        pass


class RealEnv(Env):
    logger_env: logger.Env

    def __init__(self, logger_env: logger.Env) -> None:
        super().__init__()
        self.logger_env = logger_env

    def _log(self, message: str) -> None:
        logger.log(self.logger_env, "git", message)

    def _git(self, args: str) -> List[str]:
        git_command = f"git {args}"
        self._log(f"{git_command}")
        result: subprocess.CompletedProcess[bytes] = subprocess.run(
            shlex.split(git_command),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        stdout = result.stdout
        if stdout:
            lines = stdout.decode().splitlines()
            [self._log(f"| {line}") for line in lines]
            self._log("\\------------------")
            return lines
        else:
            self._log("\\------------------")
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
    git_env: Env,
) -> GitRootDir:
    output = rev_parse(git_env, "--show-toplevel")
    if output == "":
        exit(exit_code.NOT_IN_GIT_REPO)
    return GitRootDir(output[0])


def write_patch(
    file_env: file.Env,
    patch: GitPatch,
    root_dir: GitRootDir,
) -> None:
    patches_dir = gitzen_patches(root_dir)
    if not isdir(patches_dir):
        mkdir(gitzen_refs(root_dir))
        mkdir(patches_dir)
    file.write(
        file_env,
        gitzen_patch_file(patch.zen_token, root_dir),
        [patch.hash.value],
    )


def delete_patch(zen_token: ZenToken, root_dir: GitRootDir) -> None:
    patch_file = gitzen_patch_file(zen_token, root_dir)
    if exists(patch_file):
        os.remove(patch_file)


def branch(git_env: Env) -> List[str]:
    return git_env._git("branch --no-color")


def branch_create(
    git_env: Env,
    new_branch_name: GitBranchName,
    source_branch_name: GitBranchName,
) -> List[str]:
    return git_env._git(
        f"branch {new_branch_name.value} {source_branch_name.value}",
    )


def branch_exists(
    git_env: Env,
    branch_name: GitBranchName,
) -> bool:
    lines = [line[2:] for line in branch(git_env)]
    branches = [GitBranchName(name) for name in lines]
    return branch_name in branches


def cherry_pick(
    git_env: Env,
    ref: GitBranchName,
) -> List[str]:
    return git_env._git(f"cherry-pick -x {ref.value}")


def cherry_pick_skip(
    git_env: Env,
) -> List[str]:
    return git_env._git("cherry-pick --skip")


def cherry_pick_continue(
    git_env: Env,
) -> List[str]:
    return git_env._git("cherry-pick --continue")


def config_set(
    git_env: Env,
    key: str,
    value: str,
) -> List[str]:
    return git_env._git(f"config {key} '{value}'")


def fetch(
    git_env: Env,
    remote: GitRemoteName,
) -> List[str]:
    return git_env._git(f"fetch {remote.value}")


def init(
    git_env: Env,
) -> List[str]:
    return git_env._git("init")


def init_bare(
    git_env: Env,
) -> List[str]:
    return git_env._git("init --bare")


def clone(
    git_env: Env,
    remote_repo: str,
    local_dir: str,
) -> List[str]:
    return git_env._git(f"clone {remote_repo} {local_dir}")


def add(
    git_env: Env,
    files: List[str],
) -> List[str]:
    return git_env._git(f"add {' '.join(files)}")


def commit(
    git_env: Env,
    message: List[str],
) -> List[str]:
    log = "\n".join(message)
    return git_env._git(f"commit -m'{log}'")


def commit_amend_noedit(
    git_env: Env,
) -> List[str]:
    return git_env._git("commit --amend --no-edit")


def log(
    git_env: Env,
    args: str = "",
) -> List[str]:
    return git_env._git(f"log --no-color {args}")


def status(
    git_env: Env,
) -> List[str]:
    return git_env._git("status")


def push(
    git_env: Env,
    remote: GitRemoteName,
    branch: GitBranchName,
) -> List[str]:
    return git_env._git(f"push {remote.value} {branch.value}:{branch.value}")


def rebase(
    git_env: Env,
    target: GitBranchName,
) -> List[str]:
    return git_env._git(f"rebase {target.value} --autostash")


def remote(
    git_env: Env,
) -> List[str]:
    return git_env._git("remote --verbose")


def remote_add(
    git_env: Env,
    remote_name: GitRemoteName,
    root_dir: GitRootDir,
) -> List[str]:
    return git_env._git(
        f"remote add {remote_name.value} {root_dir.value}",
    )


def rev_parse(
    git_env: Env,
    args: str = "",
) -> List[str]:
    return git_env._git(f"rev-parse {args}")


def switch(
    git_env: Env,
    branch: GitBranchName,
) -> List[str]:
    return git_env._git(f"switch {branch.value}")


def log_graph(
    git_env: Env,
) -> List[str]:
    return git_env._git("log --oneline --graph --decorate --all")
