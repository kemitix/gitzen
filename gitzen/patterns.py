commit_hash = r"[a-f0-9]{40}"
commit_log_hash = rf"^commit ({commit_hash})"
zen_token = r"(?P<zen_token>[a-f0-9]{8})"
commit_body_zen_token = rf"^(zen-token):{zen_token}$"

user = r"[a-zA-Z0-9_\-]+"
target_branch = r"(?P<target_branch>[a-zA-Z0-9_\-/\.]+)"
remote_branch = rf"^gitzen/pr/{user}/{target_branch}/{zen_token}$"
