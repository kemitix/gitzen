from gitzen.config import Config


# look for the local branch name in the remote branches from config
# if found use that, otherwise, use the default branch from Config
def getRemoteBranch(localBranch: str, config: Config) -> str:
    for remoteBranch in config.remoteBranch:
        if remoteBranch == localBranch:
            return remoteBranch
        else:
            return config.defaultRemoteBranch
    return ""
