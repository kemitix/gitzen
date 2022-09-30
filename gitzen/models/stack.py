import copy
from typing import Dict, List

from gitzen.models.git_commit import GitCommit
from gitzen.types import GitBranchName


class Stack:
    _branches: Dict[GitBranchName, List[GitCommit]]

    def __init__(self, branches: Dict[GitBranchName, List[GitCommit]]) -> None:
        self._branches = branches

    @property
    def branches(self) -> Dict[GitBranchName, List[GitCommit]]:
        return copy.deepcopy(self._branches)
