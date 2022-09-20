from typing import Dict, List

from gitzen import console, git


class FakeGitEnv(git.Env):
    requests: List[str] = []
    responses: Dict[str, List[List[str]]]
    request_counters: Dict[str, int] = {}

    def __init__(self, responses: Dict[str, List[List[str]]]) -> None:
        self.responses = responses
        for args in responses:
            self.request_counters[args] = 0

    def _git(self, console_env: console.Env, args: str) -> List[str]:
        console.log(console_env, "FakeGit", args)
        self.requests.append(args)
        if args in self.responses:
            counter = self.request_counters[args]
            if len(self.responses[args]) > counter:
                response = self.responses[args][counter]
                self.request_counters[args] += 1
                console.log(console_env, "FakeGit", f"{response}")
                return response
            console.error(
                console_env,
                f"no more responses for these args: {args}",
            )
        else:
            console.error(console_env, f"no response for these args: {args}")
        exit(1)
