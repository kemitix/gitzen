from typing import List

from gitzen.repo import getRepoDetailsFromRemote


def test_getRepoDetailsFromRemoteV():
    class TestCase:
        remote: str
        host: str
        owner: str
        name: str
        match: bool

        def __init__(
            self,
            remote: str,
            host: str,
            owner: str,
            name: str,
            match: bool,
        ):
            self.remote = remote
            self.host = host
            self.owner = owner
            self.name = name
            self.match = match

    testCases: List[TestCase] = [
        TestCase(
            "origin  https://github.com/r2/d2.git (push)",
            "github.com",
            "r2",
            "d2",
            True,
        ),
        TestCase(
            "origin  https://github.com/r2/d2.git (fetch)",
            "",
            "",
            "",
            False,
        ),
        TestCase(
            "origin  https://github.com/r2/d2 (push)",
            "github.com",
            "r2",
            "d2",
            True,
        ),
        TestCase(
            "origin  ssh://git@github.com/r2/d2.git (push)",
            "github.com",
            "r2",
            "d2",
            True,
        ),
        TestCase(
            "origin  ssh://git@github.com/r2/d2.git (fetch)",
            "",
            "",
            "",
            False,
        ),
        TestCase(
            "origin  ssh://git@github.com/r2/d2 (push)",
            "github.com",
            "r2",
            "d2",
            True,
        ),
        TestCase(
            "origin  git@github.com:r2/d2.git (push)",
            "github.com",
            "r2",
            "d2",
            True,
        ),
        TestCase(
            "origin  git@github.com:r2/d2.git (fetch)",
            "",
            "",
            "",
            False,
        ),
        TestCase(
            "origin  git@github.com:r2/d2 (push)",
            "github.com",
            "r2",
            "d2",
            True,
        ),
        TestCase(
            "origin  git@gh.enterprise.com:r2/d2.git (push)",
            "gh.enterprise.com",
            "r2",
            "d2",
            True,
        ),
        TestCase(
            "origin  git@gh.enterprise.com:r2/d2.git (fetch)",
            "",
            "",
            "",
            False,
        ),
        TestCase(
            "origin  git@gh.enterprise.com:r2/d2 (push)",
            "gh.enterprise.com",
            "r2",
            "d2",
            True,
        ),
        TestCase(
            "origin  https://github.com/r2/d2-a.git (push)",
            "github.com",
            "r2",
            "d2-a",
            True,
        ),
        TestCase(
            "origin  https://github.com/r2/d2_a.git (push)",
            "github.com",
            "r2",
            "d2_a",
            True,
        ),
    ]
    for testCase in testCases:
        host, owner, name, match = getRepoDetailsFromRemote(testCase.remote)
        assert (
            host == testCase.host
        ), f"host match failed for {testCase.remote}, got '{host}'"
        assert (
            owner == testCase.owner
        ), f"owner match failed for {testCase.remote}, got '{owner}'"
        assert (
            name == testCase.name
        ), f"name match failed for {testCase.remote}, got '{name}'"
        assert (
            match == testCase.match
        ), f"match match failed for {testCase.remote}, got '{match}'"
