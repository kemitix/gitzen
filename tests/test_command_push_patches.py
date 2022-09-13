import os
from pathlib import PosixPath
from typing import List

from faker import Faker

from gitzen import config, file
from gitzen.commands.push import update_patches
from gitzen.models.git_commit import GitCommit

# trunk-ignore(flake8/E501)
from gitzen.types import CommitBody, CommitHash, CommitTitle, CommitWipStatus, ZenToken

from .fakes.console_env import FakeConsoleEnv
from .fakes.git_env import FakeGitEnv
from .fakes.repo_files import given_repo


def test_update_patches_creates_patches(tmp_path: PosixPath) -> None:
    # given
    os.chdir(tmp_path)
    given_repo(tmp_path)
    fake = Faker()
    git_env = FakeGitEnv(
        {
            # responses go here
        }
    )
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
    cfg = config.load(console_env, f"{tmp_path}")
    # when
    update_patches(git_env, cfg, commits)
    # then
    assert file.read(
        f"{tmp_path}/.git/refs/gitzen/patches/{commits[0].zen_token.value}"
    ) == [commits[0].hash.value]
    assert file.read(
        f"{tmp_path}/.git/refs/gitzen/patches/{commits[1].zen_token.value}"
    ) == [commits[1].hash.value]
