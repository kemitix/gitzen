from typing import Any, Dict, List

from gitzen.models.git_patch import GitPatch


class ConsoleEnv:
    def _print(self, message: str) -> None:
        pass


class GitEnv:
    def _git(self, args: str) -> List[str]:
        pass

    def write_patch(self, patch: GitPatch) -> None:
        pass


class GithubEnv:
    def _graphql(
        self,
        params: Dict[str, str],
        query: str,
    ) -> Dict[str, Any]:
        pass

    def _gh(self, args: str) -> List[str]:
        pass
