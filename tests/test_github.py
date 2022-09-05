import json
import subprocess
from subprocess import CompletedProcess
from unittest import mock

from faker import Faker

from gitzen import envs, git, github
from gitzen.models.github_commit import Commit
from gitzen.models.github_info import GithubInfo
from gitzen.models.github_pull_request import PullRequest


@mock.patch("subprocess.run")
def test_fetch_info_invokes_command(mock_subproc_run) -> None:
    """
    Test that the correct command is invoked
    """
    # given
    repo_id = Faker().word()
    expected = (
        '{"data":{'
        '"viewer":{"login":"","repository":{"pullRequests":{"nodes":[]}}},'
        '"repository":{'
        f'"id":"{repo_id}"'
        "}"
        "}}"
    ).encode()
    mock_subproc_run.side_effect = [
        CompletedProcess("", 0, stdout=expected),
        CompletedProcess("", 0, stdout="* branch-name".encode()),
    ]
    # when
    github.fetch_info(
        envs.GitGithubEnv(
            git.RealGitEnv(),
            github.RealGithubEnv(),
        )
    )
    # then
    query = github.query_status
    ghApiQuery = mock.call(
        [
            "gh",
            "api",
            "graphql",
            "-F",
            "repo_owner={owner}",
            "-F",
            "repo_name={repo}",
            "-f",
            f"query={query}",
        ],
        stdout=subprocess.PIPE,
    )
    gitBranch = mock.call(
        [
            "git",
            "branch",
            "--no-color",
        ],
        stdout=subprocess.PIPE,
    )
    mock_subproc_run.assert_has_calls(
        [
            ghApiQuery,
            gitBranch,
        ]
    )


def test_json_loads__escaped_newline() -> None:
    assert json.loads('{"a":"b"}') == {"a": "b"}
    assert json.loads('{"a":"b\\nc"}') == {"a": "b\nc"}


@mock.patch("subprocess.run")
def test_fetch_info_returns_github_info(mock_subproc_run) -> None:
    """
    Test that fetchStatus parses the gh query output
    """
    # given
    mock_subproc_run.side_effect = [
        CompletedProcess(
            "",
            0,
            # trunk-ignore-begin(flake8/E501)
            stdout="""{
  "data": {
    "repository": {
      "id": "MDEwOlJlcG9zaXRvcnkyOTA1NzA4NzE="
    },
    "viewer": {
      "login": "kemitix",
      "repository": {
        "pullRequests": {
          "nodes": [
            {
              "id": "PR_kwDOEVHCd84vkAyI",
              "number": 248,
              "title": "build(deps): bump microprofile from 4.1 to 5.0 with zentoken",
              "baseRefName": "master",
              "headRefName": "gitzen/pr/master",
              "mergeable": "CONFLICTING",
              "reviewDecision": null,
              "repository": {
                "id": "MDEwOlJlcG9zaXRvcnkyOTA1NzA4NzE="
              },
              "commits": {
                "nodes": [
                  {
                    "commit": {
                      "oid": "715fbc4220806fe283e39ee74c6fca3dac52c041",
                      "messageHeadline": "build(deps): bump microprofile from 4.1 to 5.0",
                      "messageBody": "Bumps [microprofile](https://github.com/eclipse/microprofile) from 4.1 to 5.0.\\n- [Release notes](https://github.com/eclipse/microprofile/releases)\\n- [Commits](https://github.com/eclipse/microprofile/compare/4.1...5.0)\\n\\n---\\nupdated-dependencies:\\n- dependency-name: org.eclipse.microprofile:microprofile\\n  dependency-type: direct:production\\n  update-type: version-update:semver-major\\n...\\n\\nSigned-off-by: dependabot[bot] <support@github.com>\\n\\nzen-token:234ad5c1",
                      "statusCheckRollup": {
                        "state": "FAILURE"
                      }
                    }
                  }
                ]
              }
            },
            {
              "id": "PR_other",
              "number": 348,
              "title": "build(deps): bump microprofile from 4.1 to 5.0 no zentoken",
              "baseRefName": "master",
              "headRefName": "gitzen/pr/master",
              "mergeable": "CONFLICTING",
              "reviewDecision": null,
              "repository": {
                "id": "MDEwOlJlcG9zaXRvcnkyOTA1NzA4NzE="
              },
              "commits": {
                "nodes": [
                  {
                    "commit": {
                      "oid": "715fbc4220806fe283e39ee74c6fca3dac52c041",
                      "messageHeadline": "WIP build(deps): bump microprofile from 4.1 to 5.0",
                      "messageBody": "Bumps [microprofile](https://github.com/eclipse/microprofile) from 4.1 to 5.0.\\n- [Release notes](https://github.com/eclipse/microprofile/releases)\\n- [Commits](https://github.com/eclipse/microprofile/compare/4.1...5.0)\\n\\n---\\nupdated-dependencies:\\n- dependency-name: org.eclipse.microprofile:microprofile\\n  dependency-type: direct:production\\n  update-type: version-update:semver-major\\n...\\n\\nSigned-off-by: dependabot[bot] <support@github.com>",
                      "statusCheckRollup": {
                        "state": "FAILURE"
                      }
                    }
                  }
                ]
              }
            },
            {
              "id": "PR_kwDOEVHCd84vkAyI",
              "number": 248,
              "title": "build(deps): bump microprofile from 4.1 to 5.0",
              "baseRefName": "master",
              "headRefName": "gitzen/pr/other",
              "mergeable": "CONFLICTING",
              "reviewDecision": null,
              "repository": {
                "id": "MDEwOlJlcG9zaXRvcnkyOTA1NzA4NzE="
              },
              "commits": {
                "nodes": [
                  {
                    "commit": {
                      "oid": "715fbc4220806fe283e39ee74c6fca3dac52c041",
                      "messageHeadline": "build(deps): bump microprofile from 4.1 to 5.0",
                      "messageBody": "Bumps [microprofile](https://github.com/eclipse/microprofile) from 4.1 to 5.0.\\n- [Release notes](https://github.com/eclipse/microprofile/releases)\\n- [Commits](https://github.com/eclipse/microprofile/compare/4.1...5.0)\\n\\n---\\nupdated-dependencies:\\n- dependency-name: org.eclipse.microprofile:microprofile\\n  dependency-type: direct:production\\n  update-type: version-update:semver-major\\n...\\n\\nSigned-off-by: dependabot[bot] <support@github.com>",
                      "statusCheckRollup": {
                        "state": "FAILURE"
                      }
                    }
                  }
                ]
              }
            },
            {
              "id": "PR_kwDOEVHCd84vkAyI",
              "number": 248,
              "title": "build(deps): bump microprofile from 4.1 to 5.0",
              "baseRefName": "master",
              "headRefName": "gitzen/pr/other",
              "mergeable": "CONFLICTING",
              "reviewDecision": null,
              "repository": {
                "id": "invalid-repo"
              },
              "commits": {
                "nodes": [
                  {
                    "commit": {
                      "oid": "715fbc4220806fe283e39ee74c6fca3dac52c041",
                      "messageHeadline": "build(deps): bump microprofile from 4.1 to 5.0",
                      "messageBody": "Bumps [microprofile](https://github.com/eclipse/microprofile) from 4.1 to 5.0.\\n- [Release notes](https://github.com/eclipse/microprofile/releases)\\n- [Commits](https://github.com/eclipse/microprofile/compare/4.1...5.0)\\n\\n---\\nupdated-dependencies:\\n- dependency-name: org.eclipse.microprofile:microprofile\\n  dependency-type: direct:production\\n  update-type: version-update:semver-major\\n...\\n\\nSigned-off-by: dependabot[bot] <support@github.com>",
                      "statusCheckRollup": {
                        "state": "FAILURE"
                      }
                    }
                  }
                ]
              }
            },
            {
              "id": "PR_kwDOEVHCd84vkAyI",
              "number": 248,
              "title": "build(deps): bump microprofile from 4.1 to 5.0",
              "baseRefName": "master",
              "headRefName": "dependabot/maven/org.eclipse.microprofile-5.0",
              "mergeable": "CONFLICTING",
              "reviewDecision": null,
              "repository": {
                "id": "MDEwOlJlcG9zaXRvcnkyOTA1NzA4NzE="
              },
              "commits": {
                "nodes": [
                  {
                    "commit": {
                      "oid": "715fbc4220806fe283e39ee74c6fca3dac52c041",
                      "messageHeadline": "build(deps): bump microprofile from 4.1 to 5.0",
                      "messageBody": "Bumps [microprofile](https://github.com/eclipse/microprofile) from 4.1 to 5.0.\\n- [Release notes](https://github.com/eclipse/microprofile/releases)\\n- [Commits](https://github.com/eclipse/microprofile/compare/4.1...5.0)\\n\\n---\\nupdated-dependencies:\\n- dependency-name: org.eclipse.microprofile:microprofile\\n  dependency-type: direct:production\\n  update-type: version-update:semver-major\\n...\\n\\nSigned-off-by: dependabot[bot] <support@github.com>",
                      "statusCheckRollup": {
                        "state": "FAILURE"
                      }
                    }
                  }
                ]
              }
            }
          ]
        }
      }
    }
  }
}""".encode(),
            # trunk-ignore-end(flake8/E501)
        ),
        CompletedProcess("", 0, stdout="* baz".encode()),
    ]
    commit_body = (
        "Bumps [microprofile](https://github.com/eclipse/microprofile) "
        "from 4.1 to 5.0.\n"
        "- [Release notes](https://github.com/eclipse/microprofile/releases)\n"
        "- [Commits](https://github.com/eclipse/microprofile/compare/"
        "4.1...5.0)\n\n"
        "---"
        "\nupdated-dependencies:\n"
        "- dependency-name: org.eclipse.microprofile:microprofile\n"
        "  dependency-type: direct:production\n"
        "  update-type: version-update:semver-major\n"
        "...\n\n"
        "Signed-off-by: dependabot[bot] <support@github.com>"
    )
    commit_a = Commit(
        zen_token="234ad5c1",
        hash="715fbc4220806fe283e39ee74c6fca3dac52c041",
        headline="build(deps): bump microprofile from 4.1 to 5.0",
        body=commit_body + "\n\nzen-token:234ad5c1",
        wip=False,
    )
    commit_b = Commit(
        zen_token=None,
        hash="715fbc4220806fe283e39ee74c6fca3dac52c041",
        headline="WIP build(deps): bump microprofile from 4.1 to 5.0",
        body=commit_body,
        wip=True,
    )
    pull_request_a = PullRequest(
        id="PR_kwDOEVHCd84vkAyI",
        number=248,
        title="build(deps): bump microprofile from 4.1 to 5.0 with zentoken",
        baseRefName="master",
        headRefName="gitzen/pr/master",
        mergeable="CONFLICTING",
        reviewDecision="",
        repoId="MDEwOlJlcG9zaXRvcnkyOTA1NzA4NzE=",
        commits=[commit_a],
    )
    pull_request_b = github.PullRequest(
        id="PR_other",
        number=348,
        title="build(deps): bump microprofile from 4.1 to 5.0 no zentoken",
        baseRefName="master",
        headRefName="gitzen/pr/master",
        mergeable="CONFLICTING",
        reviewDecision="",
        repoId="MDEwOlJlcG9zaXRvcnkyOTA1NzA4NzE=",
        commits=[commit_b],
    )
    # when
    result = github.fetch_info(
        envs.GitGithubEnv(git.RealGitEnv(), github.RealGithubEnv())
    )
    # then
    assert len(result.pull_requests) == 2
    expected = GithubInfo(
        username="kemitix",
        repo_id="MDEwOlJlcG9zaXRvcnkyOTA1NzA4NzE=",
        local_branch="baz",
        pull_requests=[pull_request_a, pull_request_b],
    )
    assert result == expected
