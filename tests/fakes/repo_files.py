import os
import stat
import subprocess
from os import chdir
from typing import List

from gitzen import envs, file, git
from gitzen.envs import GitEnv
from gitzen.types import GitBranchName, GitRootDir


def given_repo(git_env: envs.GitEnv, dir: GitRootDir) -> None:
    chdir(dir.value)
    git.init(git_env)
    # set author identity
    git_env.git('config user.email "you@example.com"')
    git_env.git('config user.name "Your Name"')
    # install hook
    print("# install hook")
    hook = ".git/hooks/commit-msg"
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
    # create a fake origin/master
    git.branch_create(
        git_env,
        GitBranchName("origin/master"),
        GitBranchName("master"),
    )
    # create commit to represent change on local HEAD
    print("# create second commit master")
    file.write("README.md", ["Test repo"])
    git.add(git_env, ["README.md"])
    git.commit(git_env, ["Second commit"])
    show_status(git_env, dir)


def show_status(git_env: GitEnv, dir) -> None:
    ls_project_root = subprocess.run(["ls", "-la", dir.value])
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
