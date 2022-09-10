import re
from typing import List

from gitzen import patterns
from gitzen.hooks import commit_msg


def test_handle_commit_message_with_empty_body(tmp_path) -> None:
    # given
    filename = f"{tmp_path}/COMMIT_MSG"
    write_file(filename, ["Initial commit"])
    # when
    commit_msg.main([filename])
    # then
    contents = read_file(filename)
    assert contents[0] == "Initial commit"
    assert contents[1] == ""
    assert re.search(patterns.commit_body_zen_token, contents[2]) is not None
    assert len(contents) == 3


def test_handle_commit_message_with_a_body(tmp_path) -> None:
    # given
    filename = f"{tmp_path}/COMMIT_MSG"
    write_file(
        filename,
        [
            "Initial commit",
            "",
            "This does stuff.",
            "",
            "This is how...",
        ],
    )
    # when
    commit_msg.main([filename])
    # then
    contents = read_file(filename)
    assert contents[0] == "Initial commit"
    assert contents[1] == ""
    assert contents[2] == "This does stuff."
    assert contents[3] == ""
    assert contents[4] == "This is how..."
    assert contents[5] == ""
    assert re.search(patterns.commit_body_zen_token, contents[6]) is not None
    assert len(contents) == 7


def test_handle_commit_message_with_empty_body_and_token(tmp_path) -> None:
    # given
    filename = f"{tmp_path}/COMMIT_MSG"
    write_file(filename, ["Initial commit", "", "zen-token:1234abcd"])
    # when
    commit_msg.main([filename])
    # then
    contents = read_file(filename)
    assert contents[0] == "Initial commit"
    assert contents[1] == ""
    assert contents[2] == "zen-token:1234abcd"
    assert len(contents) == 3


def test_handle_commit_message_with_a_body_and_token(tmp_path) -> None:
    # given
    filename = f"{tmp_path}/COMMIT_MSG"
    write_file(
        filename,
        [
            "Initial commit",
            "",
            "This does stuff.",
            "",
            "This is how...",
            "",
            "zen-token:1234abcd",
        ],
    )
    # when
    commit_msg.main([filename])
    # then
    contents = read_file(filename)
    assert contents[0] == "Initial commit"
    assert contents[1] == ""
    assert contents[2] == "This does stuff."
    assert contents[3] == ""
    assert contents[4] == "This is how..."
    assert contents[5] == ""
    assert contents[6] == "zen-token:1234abcd"
    assert len(contents) == 7


def test_handle_interactive_rebase(tmp_path) -> None:
    # given
    filename = f"{tmp_path}/PLAN"
    write_file(
        filename,
        [
            "pick 1234567 log message 1",
            "pick 890abcd log message 2",
            "pick ef12345 log message 3",
            "",
            "# comments",
        ],
    )
    # when
    commit_msg.main([filename])
    # then
    contents = read_file(filename)
    assert contents[0] == "reword 1234567 log message 1"
    assert contents[1] == "reword 890abcd log message 2"
    assert contents[2] == "reword ef12345 log message 3"
    assert contents[3] == ""
    assert contents[4] == "# comments"
    assert len(contents) == 5


def write_file(filename: str, contents: List[str]) -> None:
    with open(filename, "w") as f:
        f.write("\n".join(contents))


def read_file(filename: str) -> List[str]:
    with open(filename, "r") as f:
        return f.read().splitlines()
