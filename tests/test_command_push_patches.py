from pathlib import PosixPath
from typing import List

from gitzen import config, file, git, logger
from gitzen.commands.push import update_patches
from gitzen.models.git_commit import GitCommit

from . import object_mother as om
from .fakes.console_env import FakeConsoleEnv
from .fakes.repo_files import given_repo


def test_update_patches_creates_patches(tmp_path: PosixPath) -> None:
    # given
    logger_env = logger.RealEnv()
    file_env = file.RealEnv(logger_env)
    git_env = git.RealEnv(logger_env)
    root_dir = given_repo(file_env, git_env, tmp_path)
    commits: List[GitCommit] = [
        om.gen_commit(token=None),
        om.gen_commit(token=None),
    ]
    console_env = FakeConsoleEnv()
    cfg = config.load(console_env, file_env, root_dir)
    # when
    update_patches(console_env, file_env, cfg.root_dir, commits)
    # then
    commit1_patch_file = git.gitzen_patch_file(commits[0].zen_token, root_dir)
    commit2_patch_file = git.gitzen_patch_file(commits[1].zen_token, root_dir)
    assert file.read(file_env, commit1_patch_file) == [commits[0].hash.value]
    assert file.read(file_env, commit2_patch_file) == [commits[1].hash.value]
