from typing import Dict, List

from gitzen import envs


class FakeGitEnv(envs.GitEnv):
    responses: Dict[str, List[List[str]]]
    request_counters: Dict[str, int] = {}

    def __init__(self, responses: Dict[str, List[List[str]]]) -> None:
        self.responses = responses
        for args in responses:
            self.request_counters[args] = 0

    def git(self, args: str) -> List[str]:
        print(f">FakeGit> {args}")
        if args in self.responses:
            counter = self.request_counters[args]
            if len(self.responses[args]) > counter:
                response = self.responses[args][counter]
                self.request_counters[args] += 1
                print(f"<FakeGit< {response}")
                return response
            print(f"ERROR: no more responses for these args: {args}")
        else:
            print(f"ERROR: no response for these args: {args}")
        exit(1)
