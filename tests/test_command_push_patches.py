from pathlib import PosixPath
from typing import List

from faker import Faker

from gitzen import config, file, git
from gitzen.commands.push import update_patches
from gitzen.models.git_commit import GitCommit

# trunk-ignore(flake8/E501)
from gitzen.types import CommitBody, CommitHash, CommitTitle, CommitWipStatus, ZenToken

from .fakes.console_env import FakeConsoleEnv
from .fakes.repo_files import given_repo


def test_update_patches_creates_patches(tmp_path: PosixPath) -> None:
    # given
    git_env = git.RealGitEnv()
    root_dir = given_repo(git_env, tmp_path)
    fake = Faker()
    commits: List[GitCommit] = [
        GitCommit(
            ZenToken(fake.word()),
            CommitHash(fake.word()),
            CommitTitle(fake.word()),
            CommitBody(fake.word()),
            CommitWipStatus(False),
        ),
        GitCommit(
            ZenToken(fake.word()),
            CommitHash(fake.word()),
            CommitTitle(fake.word()),
            CommitBody(fake.word()),
            CommitWipStatus(False),
        ),
    ]
    console_env = FakeConsoleEnv()
    cfg = config.load(console_env, root_dir)
    # when
    update_patches(cfg.root_dir, commits)
    # then
    commit1_patch_file = git.gitzen_patch_file(commits[0].zen_token, root_dir)
    commit2_patch_file = git.gitzen_patch_file(commits[1].zen_token, root_dir)
    assert file.read(commit1_patch_file) == [commits[0].hash.value]
    assert file.read(commit2_patch_file) == [commits[1].hash.value]
