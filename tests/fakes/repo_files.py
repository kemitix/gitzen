import os
import stat
import subprocess
from os import chdir
from pathlib import PosixPath
from typing import List, Tuple

from gitzen import config, console, file, git
from gitzen.types import GitBranchName, GitRemoteName, GitRootDir


def given_repo(
    file_env: file.Env,
    git_env: git.Env,
    dir: PosixPath,
) -> Tuple[GitRootDir, config.Config]:
    """
    Creates two git repos. One is bare and is included as the
    'origin' remote for the other.
    Returns the GitRootDir for the non-bare repo.
    """
    console_env = console.RealEnv(["file", "git", "given_repo"])
    console.log(console_env, "given_repo", f"BEGIN: {dir}")
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
    cfg = config.default_config(repo)
    chdir(repo_dir)
    origin = GitRemoteName("origin")
    master = GitBranchName("master")
    # set author identity
    git.config_set(git_env, "user.email", "you@example.com")
    git.config_set(git_env, "user.name", "Your Name")
    # install hook
    console.log(console_env, "given_repo", "install hook")
    hook = f"{repo_dir}/.git/hooks/commit-msg"
    project_root = os.path.realpath(os.path.dirname(__file__ + "/../../../.."))
    file.write(
        file_env,
        hook,
        [
            "#!/usr/bin/env bash",
            "echo running git zen hook",
            f"{project_root}/git-zen hook $1",
            "",
        ],
    )
    os.chmod(hook, os.stat(hook).st_mode | stat.S_IEXEC)
    subprocess.run(["cat", ".git/hooks/commit-msg"])
    show_status(console_env, git_env, repo, cfg)
    # create commit to represent remote HEAD
    console.log(console_env, "given_repo", "create first commit origin/master")
    file.write(file_env, "README.md", [])
    git.add(git_env, ["README.md"])
    git.commit(git_env, ["First commit"])
    show_status(console_env, git_env, repo, cfg)
    # push first commit to origin/master
    git.push(git_env, origin, master)
    show_status(console_env, git_env, repo, cfg)
    # create two commits to represent changes on local HEAD
    console.log(console_env, "given_repo", "create second commit master")
    file.write(file_env, "ALPHA.md", ["alpha"])
    git.add(git_env, ["ALPHA.md"])
    git.commit(git_env, ["Add ALPHA.md"])
    console.log(console_env, "given_repo", "create third commit master")
    file.write(file_env, "BETA.md", ["beta"])
    git.add(git_env, ["BETA.md"])
    git.commit(git_env, ["Add BETA.md"])
    show_status(console_env, git_env, repo, cfg)
    console.log(console_env, "given_repo", f"END: {dir}")
    return repo, cfg


def show_status(
    console_env: console.Env,
    git_env: git.Env,
    dir: GitRootDir,
    cfg: config.Config,
) -> None:
    ls_project_root = subprocess.run(["ls", "-la", dir.value])
    if ls_project_root.stdout:
        lines = ls_project_root.stdout.decode().splitlines()
        [console.log(console_env, "ls>", line) for line in lines]
    git.status(git_env)
    git.log_graph(git_env, cfg)


def given_file(file_env: file.Env, filename: str, lines: List[str]) -> None:
    with file.io_write(file_env, filename) as f:
        f.write("\n".join(lines))
