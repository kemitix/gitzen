from typing import Any, Dict, List


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


class GitGithubEnv:

    gitEnv: GitEnv
    githubEnv: GithubEnv

    def __init__(self, gitEnv: GitEnv, githubEnv: GithubEnv):
        self.gitEnv = gitEnv
        self.githubEnv = githubEnv
