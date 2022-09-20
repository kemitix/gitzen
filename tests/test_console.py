from unittest.mock import patch

from faker import Faker

from gitzen import console


@patch("builtins.print")
def test_console_info_prints(mock_print) -> None:
    # given
    message = Faker().word()
    # when
    console.info(console.RealConsoleEnv(), message)
    # then
    mock_print.assert_called_with(message)
