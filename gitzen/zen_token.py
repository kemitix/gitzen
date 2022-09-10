import re
from typing import Optional

from gitzen import patterns
from gitzen.types import ZenToken


def find_in_line(line: str) -> Optional[ZenToken]:
    matches = re.search(patterns.commit_body_zen_token, line)
    if matches:
        return ZenToken(matches.group("zen_token"))
    return None


def find_in_body(body: str) -> Optional[ZenToken]:
    for line in body.splitlines():
        token = find_in_line(line)
        if token is not None:
            return token
    return None
