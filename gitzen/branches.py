from gitzen.config import Config


# look for the local branch name in the remote branches from config
# if found use that, otherwise, use the default branch from Config
def getRemoteBranchName(localBranchName: str, config: Config) -> str:
    for remoteBranchName in config.remoteBranchNames:
        if remoteBranchName == localBranchName:
            return remoteBranchName
        else:
            return config.defaultRemoteBranch
    return ""
