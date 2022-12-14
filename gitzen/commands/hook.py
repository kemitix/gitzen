import re
from random import choice
from string import hexdigits

from gitzen import file, patterns


def main(file_env: file.Env, filename: str) -> None:
    if filename.endswith("COMMIT_EDITMSG"):
        handle_commit_message(file_env, filename)
    else:
        handle_interactive_rebase(file_env, filename)


def handle_commit_message(file_env: file.Env, filename: str) -> None:
    message = file.read(file_env, filename)
    for line in message:
        if re.search(patterns.commit_body_zen_token, line):
            # already has a zen token
            return
    message.append("")
    zen_token = gen_zen_token()
    message.append(f"zen-token:{zen_token}")
    file.write(file_env, filename, message)


# This is the only place we should be creating a zen_token value
# We want to deal with it as a str, rather then ZenToken as we
# are only about to insert the value into another str.
def gen_zen_token() -> str:
    return "".join(choice(hexdigits) for i in range(8)).lower()


def handle_interactive_rebase(file_env: file.Env, filename: str) -> None:
    plan = file.read(file_env, filename)
    update = []
    for line in plan:
        matches = re.search(patterns.rebase_pick, line)
        if matches:
            hash = matches.group("hash")
            log = matches.group("log")
            update.append(f"reword {hash} {log}")
        else:
            update.append(line)
    file.write(file_env, filename, update)
