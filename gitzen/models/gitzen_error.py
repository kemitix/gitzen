class GitZenError(Exception):
    _exit_code: int
    _message: str

    def __init__(self, exit_code: int, message: str) -> None:
        self._exit_code = exit_code
        self._message = message

    @property
    def exit_code(self) -> int:
        return self._exit_code

    @property
    def message(self) -> str:
        return self._message
