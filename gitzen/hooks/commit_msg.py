import re
from random import choice
from string import hexdigits
from typing import List

from gitzen import patterns


def main(args) -> None:
    filename = args[0]
    if filename.endswith("COMMIT_MSG"):
        handle_commit_message(filename)
    else:
        handle_interactive_rebase(filename)


def handle_commit_message(filename: str) -> None:
    message = read_file(filename)
    for line in message:
        if re.search(patterns.commit_body_zen_token, line):
            # already has a zen token
            return
    message.append("")
    zen_token = gen_zen_token()
    message.append(f"zen-token:{zen_token}")
    write_file(filename, message)


def gen_zen_token() -> str:
    return "".join(choice(hexdigits) for i in range(8)).lower()


def handle_interactive_rebase(filename: str) -> None:
    plan = read_file(filename)
    update = []
    for line in plan:
        matches = re.search(patterns.rebase_pick, line)
        if matches:
            hash = matches.group("hash")
            log = matches.group("log")
            update.append(f"reword {hash} {log}")
        else:
            update.append(line)
    write_file(filename, update)


def write_file(filename: str, contents: List[str]) -> None:
    with open(filename, "w") as f:
        f.write("\n".join(contents))


def read_file(filename: str) -> List[str]:
    with open(filename, "r") as f:
        return f.read().splitlines()
