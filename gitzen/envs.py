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


class GitGithubEnv:

    git_env: GitEnv
    github_env: GithubEnv

    def __init__(self, git_env: GitEnv, github_env: GithubEnv) -> None:
        self.git_env = git_env
        self.github_env = github_env
