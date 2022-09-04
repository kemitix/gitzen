import re
from typing import Optional


def find_in_line(line: str) -> Optional[str]:
    matches = re.search("^zen-token:(?P<token>[a-f0-9]{8})$", line)
    if matches:
        return matches.group("token")
    return None


def find_in_body(body: str) -> Optional[str]:
    for line in body.splitlines():
        token = find_in_line(line)
        if token is not None:
            return token
    return None
