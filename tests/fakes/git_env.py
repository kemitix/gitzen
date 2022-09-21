from typing import Dict, List

from gitzen import git, logger


class FakeGitEnv(git.Env):
    logger_env: logger.Env
    requests: List[str] = []
    responses: Dict[str, List[List[str]]]
    request_counters: Dict[str, int] = {}

    def __init__(
        self,
        logger_env: logger.Env,
        responses: Dict[str, List[List[str]]],
    ) -> None:
        self.logger_env = logger_env
        self.responses = responses
        for args in responses:
            self.request_counters[args] = 0

    def _git(self, args: str) -> List[str]:
        logger.log(self.logger_env, "FakeGit", args)
        self.requests.append(args)
        if args in self.responses:
            counter = self.request_counters[args]
            if len(self.responses[args]) > counter:
                response = self.responses[args][counter]
                self.request_counters[args] += 1
                logger.log(self.logger_env, "FakeGit", f"{response}")
                return response
            logger.error(
                self.logger_env,
                "FakeGit",
                f"no more responses for these args: {args}",
            )
        else:
            logger.error(
                self.logger_env,
                "FakeGit",
                f"no response for these args: {args}",
            )
        exit(1)
