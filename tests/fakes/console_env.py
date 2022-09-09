from gitzen import envs


class FakeConsoleEnv(envs.ConsoleEnv):
    std_out = []

    def say(self, message: str) -> None:
        self.std_out.append(message)
