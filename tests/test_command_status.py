from gitzen import logger
from gitzen.commands import status
from gitzen.types import GitBranchName

from . import object_mother as om
from .fakes.console_env import FakeConsoleEnv
from .fakes.git_env import FakeGitEnv
from .fakes.github_env import FakeGithubEnv


def test_command_status_fetches_info_with_pr() -> None:
    # given
    logger_env = logger.RealEnv()
    console_env = FakeConsoleEnv()
    branch_name = om.gen_git_branch_name()
    other_branch_name = om.gen_git_branch_name()
    git_env = FakeGitEnv(
        logger_env,
        {
            "branch --no-color": [
                [
                    f"* {branch_name.value}",
                    f"  {other_branch_name.value}",
                ]
            ]
        },
    )
    repo_id = om.gen_gh_repo_id()
    login = om.gen_gh_username()
    zen_token = om.gen_zen_token()
    base_ref_name = branch_name
    head_ref_name = GitBranchName(
        f"gitzen/pr/user/{base_ref_name.value}/{zen_token.value}"
    )
    commit = {
        "commit": {
            "oid": "commit-hash",
            "messageHeadline": "commit-title",
            "messageBody": "commit-body",
        }
    }
    pull_request = {
        "id": "pr-id",
        "number": "123",
        "title": "pr-title",
        "repository": {"id": repo_id.value},
        "baseRefName": base_ref_name.value,
        "headRefName": head_ref_name.value,
        "reviewDecision": "review-descision",
        "body": f"body\n\nzen-token:{zen_token.value}",
        "mergeable": "MERGEABLE",
        "commits": {"nodes": [commit]},
    }
    github_env = FakeGithubEnv(
        gh_responses={},
        gql_responses={
            repr({"repo_owner": "{owner}", "repo_name": "{repo}"}): [
                {
                    "data": {
                        "repository": {"id": repo_id.value},
                        "viewer": {
                            "login": login.value,
                            "repository": {
                                "pullRequests": {
                                    "nodes": [pull_request],
                                },
                            },
                        },
                    }
                }
            ]
        },
    )
    # when
    status.status(console_env, git_env, github_env)
    # then
    stdout = list(
        filter(lambda line: not line.startswith("Fake"), console_env.std_out),
    )
    assert stdout == [
        "Contacting Github for existing Pull Requests",
        "Found 1 Pull Requests",
        f" - {base_ref_name.value} <- {head_ref_name.value}",
        "Kept 1 Pull Requests",
        "PR-123 - MERGEABLE - pr-title",
    ]


def test_command_status_fetches_info_with_no_pr() -> None:
    # given
    logger_env = logger.RealEnv()
    console_env = FakeConsoleEnv()
    branch_name = om.gen_git_branch_name()
    other_branch_name = om.gen_git_branch_name()
    git_env = FakeGitEnv(
        logger_env,
        {
            "branch --no-color": [
                [
                    f"* {branch_name.value}",
                    f"  {other_branch_name.value}",
                ]
            ]
        },
    )
    repo_id = om.gen_gh_repo_id()
    login = om.gen_gh_username()
    zen_token = om.gen_zen_token()
    base_ref_name = branch_name
    head_ref_name = om.gen_git_branch_name()
    commit = {
        "commit": {
            "oid": "commit-hash",
            "messageHeadline": "commit-title",
            "messageBody": "commit-body",
        }
    }
    pull_request = {
        "id": "pr-id",
        "number": "123",
        "title": "pr-title",
        "repository": {"id": repo_id.value},
        "baseRefName": base_ref_name.value,
        "headRefName": head_ref_name.value,
        "reviewDecision": "review-descision",
        "body": f"body\n\nzen-token:{zen_token.value}",
        "mergeable": "MERGEABLE",
        "commits": {"nodes": [commit]},
    }
    github_env = FakeGithubEnv(
        gh_responses={},
        gql_responses={
            repr({"repo_owner": "{owner}", "repo_name": "{repo}"}): [
                {
                    "data": {
                        "repository": {"id": repo_id.value},
                        "viewer": {
                            "login": login.value,
                            "repository": {
                                "pullRequests": {
                                    "nodes": [pull_request],
                                },
                            },
                        },
                    }
                }
            ]
        },
    )
    # when
    status.status(console_env, git_env, github_env)
    # then
    stdout = list(
        filter(lambda line: not line.startswith("Fake"), console_env.std_out),
    )
    assert stdout == [
        "Contacting Github for existing Pull Requests",
        "Found 1 Pull Requests",
        f" - {base_ref_name.value} <- {head_ref_name.value}",
        "Kept 0 Pull Requests",
        "Stack is empty - no Pull Requests found",
    ]
