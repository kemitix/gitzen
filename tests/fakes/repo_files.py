import os
import stat
import subprocess
from os import chdir
from pathlib import PosixPath
from typing import List

from gitzen import envs, file, git
from gitzen.envs import GitEnv
from gitzen.types import GitBranchName, GitRemoteName, GitRootDir


def given_repo(git_env: envs.GitEnv, dir: PosixPath) -> GitRootDir:
    """
    Creates two git repos. One is bare and is included as the
    'origin' remote for the other.
    Returns the GitRootDir for the non-bare repo.
    """
    print(f"\ngiven_repo> BEGIN {dir}")
    # create origin bare repo
    origin_dir = f"{dir}/origin"
    os.mkdir(origin_dir)
    chdir(origin_dir)
    git.init_bare(git_env)
    # create main repo
    repo_dir = f"{dir}/repo"
    chdir(dir)
    git.clone(git_env, origin_dir, "repo")
    repo = GitRootDir(repo_dir)
    chdir(repo_dir)
    origin = GitRemoteName("origin")
    master = GitBranchName("master")
    # set author identity
    git_env.git('config user.email "you@example.com"')
    git_env.git('config user.name "Your Name"')
    # install hook
    print("# install hook")
    hook = f"{repo_dir}/.git/hooks/commit-msg"
    project_root = os.path.realpath(os.path.dirname(__file__ + "/../../../.."))
    file.write(
        hook,
        [
            "#!/usr/bin/env bash",
            "echo running gz hook",
            f"{project_root}/gz hook $1",
            "",
        ],
    )
    os.chmod(hook, os.stat(hook).st_mode | stat.S_IEXEC)
    subprocess.run(["cat", ".git/hooks/commit-msg"])
    show_status(git_env, dir)
    # create commit to represent remote HEAD
    print("# create first commit origin/master")
    file.write("README.md", [])
    git.add(git_env, ["README.md"])
    git.commit(git_env, ["First commit"])
    show_status(git_env, dir)
    # push first commit to origin/master
    git.push(git_env, origin, master)
    show_status(git_env, dir)
    # create two commits to represent changes on local HEAD
    print("# create second commit master")
    file.write("ALPHA.md", ["alpha"])
    git.add(git_env, ["ALPHA.md"])
    git.commit(git_env, ["Add ALPHA.md"])

    print("# create third commit master")
    file.write("BETA.md", ["beta"])
    git.add(git_env, ["BETA.md"])
    git.commit(git_env, ["Add BETA.md"])
    show_status(git_env, dir)
    print(f"given_repo> END {dir}\n")
    return repo


def show_status(git_env: GitEnv, dir: PosixPath) -> None:
    ls_project_root = subprocess.run(["ls", "-la", dir])
    if ls_project_root.stdout:
        lines = ls_project_root.stdout
        [print(f"ls> {line}") for line in lines]
    [print(f"git status> {line}") for line in git.status(git_env)]
    [
        print(f"git log> {line}")
        for line in git_env.git("log --oneline --graph --decorate --all")
    ]


def given_file(file: str, lines: List[str]) -> None:
    with open(file, "w") as fp:
        contents = "\n".join(lines)
        fp.write(contents)
