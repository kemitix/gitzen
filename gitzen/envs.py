from typing import Any, Dict, List

from gitzen import console


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
