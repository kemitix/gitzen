class Env:
    def _print(self, message: str) -> None:
        pass


class RealEnv(Env):
    def _print(self, message: str) -> None:
        print(message)


def info(console_env: Env, message: str) -> None:
    console_env._print(message)


def error(console_env: Env, message: str) -> None:
    console_env._print(f"ERROR: {message}")


def log(console_env: Env, section: str, message: str) -> None:
    console_env._print(f"{section}> {message}")
