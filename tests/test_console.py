from unittest.mock import patch

from faker import Faker

from gitzen.console import RealConsoleEnv, say


@patch("builtins.print")
def test_console_say_prints(mock_print) -> None:
    # given
    console = RealConsoleEnv()
    message = Faker().word()
    # when
    say(console, message)
    # then
    mock_print.assert_called_with(message)
