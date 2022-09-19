from gitzen.envs import ConsoleEnv


class RealConsoleEnv(ConsoleEnv):
    def _print(self, message: str) -> None:
        print(message)


def info(console_env: ConsoleEnv, message: str) -> None:
    console_env._print(message)
