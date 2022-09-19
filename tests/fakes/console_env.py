from gitzen import envs


class FakeConsoleEnv(envs.ConsoleEnv):
    def __init__(self) -> None:
        super().__init__()
        self.std_out = []

    def _print(self, message: str) -> None:
        self.std_out.append(message)
