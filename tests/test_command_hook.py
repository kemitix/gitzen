import re

from gitzen import cli, file, patterns


def test_handle_commit_message_with_empty_body(tmp_path) -> None:
    # given
    filename = f"{tmp_path}/COMMIT_MSG"
    file.write(filename, ["Initial commit"])
    # when
    cli.main(["", "hook", filename])
    # then
    contents = file.read(filename)
    assert contents[0] == "Initial commit"
    assert contents[1] == ""
    assert re.search(patterns.commit_body_zen_token, contents[2]) is not None
    assert len(contents) == 3


def test_handle_commit_message_with_a_body(tmp_path) -> None:
    # given
    filename = f"{tmp_path}/COMMIT_MSG"
    file.write(
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
    cli.main(["", "hook", filename])
    # then
    contents = file.read(filename)
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
    file.write(filename, ["Initial commit", "", "zen-token:1234abcd"])
    # when
    cli.main(["", "hook", filename])
    # then
    contents = file.read(filename)
    assert contents[0] == "Initial commit"
    assert contents[1] == ""
    assert contents[2] == "zen-token:1234abcd"
    assert len(contents) == 3


def test_handle_commit_message_with_a_body_and_token(tmp_path) -> None:
    # given
    filename = f"{tmp_path}/COMMIT_MSG"
    file.write(
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
    cli.main(["", "hook", filename])
    # then
    contents = file.read(filename)
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
    file.write(
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
    cli.main(["", "hook", filename])
    # then
    contents = file.read(filename)
    assert contents[0] == "reword 1234567 log message 1"
    assert contents[1] == "reword 890abcd log message 2"
    assert contents[2] == "reword ef12345 log message 3"
    assert contents[3] == ""
    assert contents[4] == "# comments"
    assert len(contents) == 5
