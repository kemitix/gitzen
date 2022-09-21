from typing import List


class Env:
    def _print(self, message: str) -> None:
        pass

    def _print_log(self, section: str, message: str) -> None:
        pass


class RealEnv(Env):
    log_sections: List[str]

    def __init__(self, sections: List[str] = ["all"]) -> None:
        super().__init__()
        self.log_sections = sections

    def _print(self, message: str) -> None:
        print(message)

    def _print_log(self, section: str, message: str) -> None:
        if section in self.log_sections:
            log_line = f"{section}> {message}"
            self._print(log_line)


def info(console_env: Env, message: str) -> None:
    console_env._print(message)


def error(console_env: Env, message: str) -> None:
    console_env._print(f"ERROR: {message}")


def log(console_env: Env, section: str, message: str) -> None:
    console_env._print_log(section, message)
