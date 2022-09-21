from typing import IO, Any, List

from gitzen import logger


class Env:
    def write(self, filename: str, contents: List[str]) -> None:
        pass

    def read(self, filename: str) -> List[str]:
        pass

    def open(self, filename: str, mode: str) -> IO[Any]:
        pass


class RealEnv(Env):
    logger_env: logger.Env

    def __init__(self, logger_env: logger.Env) -> None:
        super().__init__()
        self.logger_env = logger_env

    def _log(self, message: str) -> None:
        logger.log(self.logger_env, "file", message)

    def write(self, filename: str, contents: List[str]) -> None:
        self._log(f"write '{filename}'")
        [self._log(f"| {line}") for line in contents]
        with open(filename, "w") as f:
            f.write("\n".join(contents))

    def read(self, filename: str) -> List[str]:
        self._log(f"read '{filename}'")
        with open(filename, "r") as f:
            contents = f.read().splitlines()
            [self._log(f"| {line}") for line in contents]
            return contents

    def open(self, filename: str, mode: str) -> IO[Any]:
        self._log(f"open '{filename}' [{mode}]")
        return open(filename, mode)


def write(env: Env, filename: str, contents: List[str]) -> None:
    env.write(filename, contents)


def read(env: Env, filename: str) -> List[str]:
    return env.read(filename)


def io_read(env: Env, filename: str) -> IO[Any]:
    return env.open(filename, "r")


def io_write(env: Env, filename: str) -> IO[Any]:
    return env.open(filename, "w")
