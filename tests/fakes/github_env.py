import re
from typing import Any, Dict, List

from gitzen import envs


class MuteFakeGuthubEnv(envs.GithubEnv):
    requests: List[str]

    def __init__(self) -> None:
        super().__init__()
        self.requests = []

    def _gh(self, args: str) -> List[str]:
        self.requests.append(args)
        return []


class FakeGithubEnv(envs.GithubEnv):
    gh_responses: Dict[str, List[List[str]]]
    gh_request_counters: Dict[str, int] = {}
    gql_responses: Dict[str, List[Any]]
    gql_request_counters: Dict[str, int] = {}
    # prs closed: a list of PR#
    closed_with_comment: Dict[int, str] = {}

    def __init__(
        self,
        gh_responses: Dict[str, List[List[str]]],
        gql_responses: Dict[str, List[Any]],
    ) -> None:
        self.gh_responses = gh_responses
        for args in gh_responses:
            self.gh_request_counters[args] = 0
        self.gql_responses = gql_responses
        for args in gql_responses:
            self.gql_request_counters[args] = 0

    def _gh(self, args: str) -> List[str]:
        print(f">FakeGithub>GH> {args}")
        close_with_comment_matches = re.search(
            "pr close (?P<pr>\\d+) --comment '(?P<comment>.*)'",
            args,
        )
        if close_with_comment_matches:
            pr: int = close_with_comment_matches.group("pr")
            comment = close_with_comment_matches.group("comment")
            print(f"TEST: close {pr} with comment: {comment}")
            self.closed_with_comment[pr] = comment
        else:
            print(f"TEST: unknown command: {args}")
        if args in self.gh_responses:
            counter = self.gh_request_counters[args]
            if len(self.gh_responses[args]) > counter:
                response = self.gh_responses[args][counter]
                self.gh_request_counters[args] += 1
                print(f"<FakeGit<GH< {response}")
                return response
            print(f"ERROR: no more responses for these args: {args}")
        else:
            print(f"ERROR: no response for these args: {args}")
        exit(1)

    def _graphql(
        self,
        params: Dict[str, str],
        query: str,
    ) -> Dict[str, Any]:
        args = repr(params)
        print(f">FakeGithub>GQL> {args}")
        if args in self.gql_responses:
            counter = self.gql_request_counters[args]
            if len(self.gql_responses[args]) > counter:
                response = self.gql_responses[args][counter]
                self.gql_request_counters[args] += 1
                print(f"<FakeGithub<GQL< {response}")
                return response
            print(f"ERROR: no more responses for these args: {args}")
        else:
            print(f"ERROR: no response for these args: {args}")
        exit(1)

    def __repr__(self) -> str:
        return (
            "FakeGithubEnv("
            f"closed_with_comment: {repr(self.closed_with_comment)}"
            ")"
        )
