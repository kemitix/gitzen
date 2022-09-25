from typing import List


class Env:
    def log(self, section: str, message: str) -> None:
        pass

    def error(self, section: str, message: str) -> None:
        pass


class RealEnv(Env):
    sections: List[str]

    def __init__(self, sections: List[str] = ["all"]) -> None:
        super().__init__()
        self.sections = sections

    def log(self, section: str, message: str) -> None:
        if "all" in self.sections or section in self.sections:
            log_line = f"{section}> {message}"
            print(log_line)

    def error(self, section: str, message: str) -> None:
        log_line = f"ERROR:{section} > {message}"
        print(log_line)


def log(logger_env: Env, section: str, message: str) -> None:
    logger_env.log(section, message)


def error(logger_env: Env, section: str, message: str) -> None:
    logger_env.error(section, message)


def line_contains(needle: str, log: List[str]) -> bool:
    for line in log:
        if needle in line:
            return True
    return False
