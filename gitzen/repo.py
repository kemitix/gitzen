from os import error
from gitzen import git

def localBranch() -> str:
    branches = git.branch()
    for branch in branches:
        if branch.startswith('* '):
            return branch.removeprefix('* ')
    error("Can't find local branch name")
    exit
