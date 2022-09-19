from unittest.mock import patch

from faker import Faker

from gitzen.console import RealConsoleEnv, info


@patch("builtins.print")
def test_console_say_prints(mock_print) -> None:
    # given
    console = RealConsoleEnv()
    message = Faker().word()
    # when
    info(console, message)
    # then
    mock_print.assert_called_with(message)
