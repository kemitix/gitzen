from pathlib import PosixPath

from gitzen import config, console, file, git, logger
from gitzen.push.commits import scan
from gitzen.types import CommitTitle, GitBranchName

from .fakes.repo_files import given_repo, given_repo_advanced


def test_scans_default(tmp_path: PosixPath) -> None:
    # given
    console_env = console.RealEnv()
    logger_env = logger.RealEnv()
    file_env = file.RealEnv(logger_env)
    git_env = git.RealEnv(logger_env)
    root_dir = given_repo(file_env, git_env, tmp_path)
    cfg = config.default_config(root_dir)
    # when
    result = scan(console_env, git_env, cfg)
    # then
    master = GitBranchName("master")
    assert master in result
    branch = result[master]
    assert len(branch) == 2
    alpha = branch[0]
    assert alpha.messageHeadline == CommitTitle("Add ALPHA.md")
    beta = branch[1]
    assert beta.messageHeadline == CommitTitle("Add BETA.md")


def test_scans_default_and_remotes(tmp_path):
    # given
    console_env = console.RealEnv()
    logger_env = logger.RealEnv()
    file_env = file.RealEnv(logger_env)
    git_env = git.RealEnv(logger_env)
    root_dir = given_repo_advanced(file_env, git_env, tmp_path, 3)
    file.write(
        file_env,
        ".gitzen.yml",
        [
            "remote: origin",
            "defaultBranch: master",
            "remoteBranches:",
            "  - branch-1",
        ],
    )
    git.log_graph(git_env)
    cfg = config.load(console_env, file_env, root_dir)
    # when
    result = scan(console_env, git_env, cfg)
    # then

    master = GitBranchName("master")
    assert master in result
    branch = result[master]
    assert len(branch) == 2
    first = branch[0]
    assert first.messageHeadline == CommitTitle("Add ALPHA.md")
    second = branch[1]
    assert second.messageHeadline == CommitTitle("Add BETA.md")

    assert GitBranchName("branch-0") not in result

    branch1 = GitBranchName("branch-1")
    assert branch1 in result
    branch = result[branch1]
    assert len(branch) == 2
    first = branch[0]
    assert first.messageHeadline == CommitTitle("Add branch-1-file-0.md")
    second = branch[1]
    assert second.messageHeadline == CommitTitle("Add branch-1-file-1.md")

    assert GitBranchName("branch-2") not in result
