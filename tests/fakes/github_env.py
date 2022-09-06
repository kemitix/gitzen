import re
from typing import Dict, List

from gitzen import envs


class FakeGithubEnv(envs.GithubEnv):
    # prs closed: a list of PR#
    closed_with_comment: Dict[int, str] = {}

    def gh(self, args: str) -> List[str]:
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
        return []

    def __repr__(self) -> str:
        return (
            "FakeGithubEnv("
            f"closed_with_comment: {repr(self.closed_with_comment)}"
            ")"
        )
