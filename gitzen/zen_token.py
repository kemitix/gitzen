import re
from typing import Optional, Union

from gitzen import patterns
from gitzen.types import CommitBody, PullRequestBody, ZenToken


def find_in_line(line: str) -> Optional[ZenToken]:
    matches = re.search(patterns.commit_body_zen_token, line)
    if matches:
        return ZenToken(matches.group("zen_token"))
    return None


def find_in_body(
    body: Union[CommitBody, PullRequestBody],
) -> Optional[ZenToken]:
    for line in body.value.splitlines():
        token = find_in_line(line)
        if token is not None:
            return token
    return None
