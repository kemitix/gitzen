from typing import IO, Any, List


class Env:
    def write(self, filename: str, contents: List[str]) -> None:
        pass

    def read(self, filename: str) -> List[str]:
        pass

    def open(self, filename: str, mode: str) -> IO[Any]:
        pass


class RealEnv(Env):
    def write(self, filename: str, contents: List[str]) -> None:
        with open(filename, "w") as f:
            f.write("\n".join(contents))

    def read(self, filename: str) -> List[str]:
        with open(filename, "r") as f:
            return f.read().splitlines()

    def open(self, filename: str, mode: str) -> IO[Any]:
        return open(filename, mode)


def write(env: Env, filename: str, contents: List[str]) -> None:
    env.write(filename, contents)


def read(env: Env, filename: str) -> List[str]:
    return env.read(filename)


def io_read(env: Env, filename: str) -> IO[Any]:
    return env.open(filename, "r")


def io_write(env: Env, filename: str) -> IO[Any]:
    return env.open(filename, "w")
