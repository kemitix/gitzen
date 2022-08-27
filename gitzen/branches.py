from gitzen.config import GitZenConfig

# look for the local branch name in the remote branches from config
# if found use that, otherwise, use the default branch from Config
def getRemoteBranchName(localBranchName: str, config: GitZenConfig) -> str:
    for remoteBranchName in config.remoteBranchNames:
        if remoteBranchName == localBranchName:
            return remoteBranchName
        else:
            return config.defaultRemoteBranch
    return ""

