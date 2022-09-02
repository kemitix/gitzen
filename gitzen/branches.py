from gitzen.config import Config


# look for the local branch name in the remote branches from config
# if found use that, otherwise, use the default branch from Config
def get_remote_branch(local_branch: str, config: Config) -> str:
    for remote_branch in config.remote_branch:
        if remote_branch == local_branch:
            return remote_branch
        else:
            return config.default_remote_branch
    return ""
