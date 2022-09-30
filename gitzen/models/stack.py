import copy
from typing import Dict, List, Optional

from gitzen.models.git_commit import GitCommit
from gitzen.types import GitBranchName, ZenToken


class Stack:
    _branches: Dict[GitBranchName, List[GitCommit]]
    _tokens: Dict[ZenToken, GitCommit]

    def __init__(self, branches: Dict[GitBranchName, List[GitCommit]]) -> None:
        self._branches = branches
        tokens = {}
        for branch in branches:
            for commit in branches[branch]:
                tokens[commit.zen_token] = commit
        self._tokens = tokens

    def branch(self, branch: GitBranchName) -> List[GitCommit]:
        if branch in self._branches:
            return copy.deepcopy(self._branches[branch])
        return []

    @property
    def branches(self) -> Dict[GitBranchName, List[GitCommit]]:
        return copy.deepcopy(self._branches)

    def token(self, token: ZenToken) -> Optional[GitCommit]:
        return self._tokens.get(token)

    @property
    def tokens(self) -> Dict[ZenToken, GitCommit]:
        return copy.deepcopy(self._tokens)
