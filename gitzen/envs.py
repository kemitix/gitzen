from typing import Any, Dict, List

from gitzen import console
from gitzen.models.git_patch import GitPatch


class GitEnv:
    def _git(
        self,
        console_env: console.Env,
        args: str,
    ) -> List[str]:
        pass

    def write_patch(self, patch: GitPatch) -> None:
        pass


class GithubEnv:
    def _graphql(
        self,
        console_env: console.Env,
        params: Dict[str, str],
        query: str,
    ) -> Dict[str, Any]:
        pass

    def _gh(
        self,
        console_env: console.Env,
        args: str,
    ) -> List[str]:
        pass
