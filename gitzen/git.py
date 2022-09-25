import os
import shlex
import subprocess
from os import mkdir
from os.path import isdir
from typing import List, Optional, Tuple

from genericpath import exists

from gitzen import exit_code, file, logger
from gitzen.models.git_patch import GitPatch
from gitzen.models.gitzen_error import GitZenError

# trunk-ignore(flake8/E501)
from gitzen.types import CommitHash, GitBranchName, GitRemoteName, GitRootDir, ZenToken


class Env:
    def _git(self, args: str) -> Tuple[Optional[int], List[str]]:
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

    def _error(self, message: str) -> None:
        logger.error(self.logger_env, "git", message)

    def _git(self, args: str) -> Tuple[Optional[int], List[str]]:
        git_command = f"git {args}"
        self._log(f"{git_command}")
        result: subprocess.CompletedProcess[bytes] = subprocess.run(
            shlex.split(git_command),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        code = None if result.returncode == 0 else result.returncode
        stdout = result.stdout
        if stdout:
            lines = stdout.decode().splitlines()
            [self._log(f"| {line}") for line in lines]
            self._log("\\------------------")
            return code, lines
        else:
            self._log("\\------------------")
            return code, []


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


def outdated_patch(
    file_env: file.Env,
    patch: GitPatch,
    root_dir: GitRootDir,
) -> bool:
    filename = gitzen_patch_file(patch.zen_token, root_dir)
    if os.path.exists(filename):
        hashes = file.read(file_env, filename)
        hash = CommitHash(hashes[0])
        return hash != patch.hash
    return True


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


def branch(git_env: Env) -> Tuple[Optional[int], List[str]]:
    return git_env._git("branch --no-color")


def branch_create(
    git_env: Env,
    new_branch_name: GitBranchName,
    source_branch_name: GitBranchName,
) -> List[str]:
    rc, log = git_env._git(
        f"branch {new_branch_name.value} {source_branch_name.value}",
    )
    if rc:
        raise GitZenError(
            rc,
            f"Unable to create branch {new_branch_name.value}",
        )
    return log


def branch_delete(
    git_env: Env,
    branch: GitBranchName,
) -> List[str]:
    return git_env._git(f"branch -d {branch.value}")[1]


def branch_exists(
    git_env: Env,
    branch_name: GitBranchName,
) -> bool:
    _, log = branch(git_env)
    lines = [line[2:] for line in log]
    branches = [GitBranchName(name) for name in lines]
    return branch_name in branches


def cherry_pick(
    git_env: Env,
    ref: GitBranchName,
) -> List[str]:
    return git_env._git(
        f"cherry-pick --allow-empty --allow-empty-message -x {ref.value}"
    )[1]


def cherry_pick_skip(
    git_env: Env,
) -> List[str]:
    return git_env._git("cherry-pick --skip")[1]


def cherry_pick_continue(
    git_env: Env,
) -> List[str]:
    return git_env._git("cherry-pick --continue")[1]


def config_set(
    git_env: Env,
    key: str,
    value: str,
) -> List[str]:
    return git_env._git(f"config {key} '{value}'")[1]


def fetch(
    git_env: Env,
    remote: GitRemoteName,
) -> List[str]:
    rc, log = git_env._git(f"fetch {remote.value}")
    if rc:
        raise GitZenError(rc, f"Unable to fetch from remote {remote.value}")
    return log


def init(
    git_env: Env,
) -> List[str]:
    return git_env._git("init")[1]


def init_bare(
    git_env: Env,
) -> List[str]:
    return git_env._git("init --bare")[1]


def clone(
    git_env: Env,
    remote_repo: str,
    local_dir: str,
) -> List[str]:
    return git_env._git(f"clone {remote_repo} {local_dir}")[1]


def add(
    git_env: Env,
    files: List[str],
) -> List[str]:
    return git_env._git(f"add {' '.join(files)}")[1]


def commit(
    git_env: Env,
    message: List[str],
) -> List[str]:
    log = "\n".join(message)
    rc, log = git_env._git(f"commit -m'{log}'")
    if rc:
        raise GitZenError(rc, "Unable to commit local changes")
    return log


def commit_amend_noedit(
    git_env: Env,
) -> List[str]:
    return git_env._git("commit --amend --no-edit")[1]


def log(
    git_env: Env,
    args: str = "",
) -> List[str]:
    return git_env._git(f"log --no-color {args}")[1]


def status(
    git_env: Env,
) -> List[str]:
    return git_env._git("status")[1]


def pull(
    git_env: Env,
    remote: GitRemoteName,
    branch: GitBranchName,
) -> List[str]:
    return git_env._git(f"pull {remote.value} {branch.value}")[1]


def push(
    git_env: Env,
    remote: GitRemoteName,
    branch: GitBranchName,
) -> List[str]:
    return git_env._git(
        f"push {remote.value} {branch.value}:{branch.value}",
    )[1]


def rebase(
    git_env: Env,
    target: GitBranchName,
) -> List[str]:
    rc, log = git_env._git(f"rebase {target.value} --autostash")
    if rc:
        raise GitZenError(rc, f"Unable to rebase on {target.value}")
    return log


def remote(
    git_env: Env,
) -> List[str]:
    return git_env._git("remote --verbose")[1]


def remote_add(
    git_env: Env,
    remote_name: GitRemoteName,
    root_dir: GitRootDir,
) -> List[str]:
    return git_env._git(
        f"remote add {remote_name.value} {root_dir.value}",
    )[1]


def reset_hard(
    git_env: Env,
    base: GitBranchName,
) -> List[str]:
    return git_env._git(f"reset --hard {base.value}")[1]


def restore_staged_worktree(
    git_env: Env,
    source: GitBranchName,
) -> List[str]:
    return git_env._git(
        f"restore --staged --worktree --source {source.value} .",
    )[1]


def rev_parse(
    git_env: Env,
    args: str = "",
) -> List[str]:
    return git_env._git(f"rev-parse {args}")[1]


def switch(
    git_env: Env,
    branch: GitBranchName,
) -> List[str]:
    rc, log = git_env._git(f"switch {branch.value}")
    if rc:
        raise GitZenError(rc, f"Unable to switch to branch {branch.value}")
    return log


def log_graph(
    git_env: Env,
) -> List[str]:
    return git_env._git("log --oneline --graph --decorate --all")[1]
