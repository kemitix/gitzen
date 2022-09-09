from gitzen.envs import ConsoleEnv


class RealConsoleEnv(ConsoleEnv):
    def say(self, message: str) -> None:
        print(message)


def say(console_env: ConsoleEnv, message: str) -> None:
    console_env.say(message)
