import os
import stat
from os import chdir
from typing import List

from gitzen import envs, file, git
from gitzen.types import GitBranchName, GitRootDir


def given_repo(git_env: envs.GitEnv, dir: GitRootDir) -> None:
    chdir(dir.value)
    git.init(git_env)
    # install hook
    project_root = os.path.realpath(os.path.dirname(__file__ + "/../../../.."))
    hook = ".git/hooks/commit-msg"
    file.write(hook, [f"{project_root}/gz hook $1"])
    os.chmod(hook, os.stat(hook).st_mode | stat.S_IEXEC)
    # create commit to represent remote HEAD
    file.write("README.md", [])
    git.add(git_env, ["README.md"])
    git.commit(git_env, ["Initial commit"])
    # create a fake origin/master
    git.branch_create(
        git_env,
        GitBranchName("origin/master"),
        GitBranchName("master"),
    )
    # create commit to represent change on local HEAD
    file.write("README.md", ["Test repo"])
    git.add(git_env, ["README.md"])
    git.commit(git_env, ["Second commit"])


def given_file(file: str, lines: List[str]) -> None:
    with open(file, "w") as fp:
        contents = "\n".join(lines)
        fp.write(contents)
