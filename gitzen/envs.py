from typing import Any, Dict, List


class ConsoleEnv:
    def say(self, message: str) -> None:
        pass


class GitEnv:
    def git(self, args: str) -> List[str]:
        pass


class GithubEnv:
    def graphql(
        self,
        params: Dict[str, str],
        query: str,
    ) -> Dict[str, Any]:
        pass

    def gh(self, args: str) -> List[str]:
        pass
