import json
from subprocess import CompletedProcess
from unittest import mock

from gitzen import github

@mock.patch('subprocess.run')
def test_pullRequests(mock_subproc_run):
    """
    Test that the correct command is invoked
    """
    #given
    mock_subproc_run.return_value = CompletedProcess("", 0, 
        stdout='{"data":{"viewer":{"repository": {"pullRequests": {"nodes":[]}}}}}'.encode())
    #when
    github.pullRequests()
    #then
    query = github.queryPullRequests
    mock_subproc_run.assert_called_with(['gh', 'api', 'graphql', '-F', "repo_name={repo}", '-f', f"query={query}"])

def test_json_loads__escaped_newline():
    assert json.loads('{"a":"b"}') == {"a": "b"}
    assert json.loads('{"a":"b\\nc"}') == {"a": "b\nc"}

@mock.patch('subprocess.run')
def test_pullRequests_returns_list_of_prs(mock_subproc_run):
    """
    Test the pullRequests parses the prs from the gh query output
    """
    #given
    mock_subproc_run.return_value = CompletedProcess("", 0, 
        stdout="""{
  "data": {
    "viewer": {
      "repository": {
        "pullRequests": {
          "nodes": [
            {
              "id": "PR_kwDOEVHCd84vkAyI",
              "number": 248,
              "title": "build(deps): bump microprofile from 4.1 to 5.0",
              "baseRefName": "master",
              "headRefName": "dependabot/maven/org.eclipse.microprofile-microprofile-5.0",
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
}""".encode())
    #when
    result = github.pullRequests()
    #then
    assert result == [github.PullRequest(
        id = "PR_kwDOEVHCd84vkAyI",
        number = 248,
        title = "build(deps): bump microprofile from 4.1 to 5.0",
        baseRefName = "master",
        headRefName = "dependabot/maven/org.eclipse.microprofile-microprofile-5.0",
        mergeable = "CONFLICTING",
        reviewDecision = "",
        repoId = "MDEwOlJlcG9zaXRvcnkyOTA1NzA4NzE=",
        commits = [github.Commit(
            oid = "715fbc4220806fe283e39ee74c6fca3dac52c041",
            messageHeadline = "build(deps): bump microprofile from 4.1 to 5.0",
            messageBody = "Bumps [microprofile](https://github.com/eclipse/microprofile) from 4.1 to 5.0.\n- [Release notes](https://github.com/eclipse/microprofile/releases)\n- [Commits](https://github.com/eclipse/microprofile/compare/4.1...5.0)\n\n---\nupdated-dependencies:\n- dependency-name: org.eclipse.microprofile:microprofile\n  dependency-type: direct:production\n  update-type: version-update:semver-major\n...\n\nSigned-off-by: dependabot[bot] <support@github.com>",
            status = "FAILURE"
        )]
    )]
