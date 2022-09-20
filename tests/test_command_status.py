from faker import Faker

from gitzen.commands import status

from .fakes.console_env import FakeConsoleEnv
from .fakes.git_env import FakeGitEnv
from .fakes.github_env import FakeGithubEnv


def test_command_status_fetches_info_with_pr() -> None:
    # given
    fake = Faker()
    console_env = FakeConsoleEnv()
    branch_name = fake.word()
    other_branch_name = fake.word()
    git_env = FakeGitEnv(
        {
            "branch --no-color": [
                [
                    f"* {branch_name}",
                    f"  {other_branch_name}",
                ]
            ]
        }
    )
    repo_id = fake.word()
    login = fake.word()
    zen_token = "1234abcd"
    base_ref_name = branch_name
    head_ref_name = f"gitzen/pr/user/{base_ref_name}/{zen_token}"
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
        "repository": {"id": repo_id},
        "baseRefName": base_ref_name,
        "headRefName": head_ref_name,
        "reviewDecision": "review-descision",
        "body": f"body\n\nzen-token:{zen_token}",
        "mergeable": "MERGEABLE",
        "commits": {"nodes": [commit]},
    }
    github_env = FakeGithubEnv(
        gh_responses={},
        gql_responses={
            repr({"repo_owner": "{owner}", "repo_name": "{repo}"}): [
                {
                    "data": {
                        "repository": {"id": repo_id},
                        "viewer": {
                            "login": login,
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
        "Querying Github...",
        "Found 1 prs",
        f"{base_ref_name} <- {head_ref_name}",
        "Kept 1 prs",
        "PR-123 - MERGEABLE - pr-title",
    ]


def test_command_status_fetches_info_with_no_pr() -> None:
    # given
    fake = Faker()
    console_env = FakeConsoleEnv()
    branch_name = fake.word()
    other_branch_name = fake.word()
    git_env = FakeGitEnv(
        {
            "branch --no-color": [
                [
                    f"* {branch_name}",
                    f"  {other_branch_name}",
                ]
            ]
        }
    )
    repo_id = fake.word()
    login = fake.word()
    zen_token = "1234abcd"
    base_ref_name = branch_name
    head_ref_name = "non-gitzen/pr/123"
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
        "repository": {"id": repo_id},
        "baseRefName": base_ref_name,
        "headRefName": head_ref_name,
        "reviewDecision": "review-descision",
        "body": f"body\n\nzen-token:{zen_token}",
        "mergeable": "MERGEABLE",
        "commits": {"nodes": [commit]},
    }
    github_env = FakeGithubEnv(
        gh_responses={},
        gql_responses={
            repr({"repo_owner": "{owner}", "repo_name": "{repo}"}): [
                {
                    "data": {
                        "repository": {"id": repo_id},
                        "viewer": {
                            "login": login,
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
        "Querying Github...",
        "Found 1 prs",
        f"{base_ref_name} <- {head_ref_name}",
        "github.fetch_info> unknown head_ref: non-gitzen/pr/123",
        "Kept 0 prs",
        "Stack is empty - no PRs found",
    ]
