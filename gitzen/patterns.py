commit_hash = r"[a-f0-9]{40}"
short_hash = r"[a-f0-9]{7}"
commit_log_hash = rf"^commit ({commit_hash})"
zen_token = r"(?P<zen_token>[a-f0-9]{8})"
commit_body_zen_token = rf"^(zen-token):{zen_token}$"

user = r"[a-zA-Z0-9_\-]+"
branch_name = r"(?P<target_branch>[a-zA-Z0-9_\-/\.]+)"
remote_pr_branch = rf"^gitzen/pr/{user}/{branch_name}/{zen_token}$"
remote_patch_branch = rf"^gitzen/patch/{user}/{zen_token}$"

rebase_pick = rf"^pick\s+(?P<hash>{short_hash})\s+(?P<log>.*)$"
