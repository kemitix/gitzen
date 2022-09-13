from gitzen.types import CommitHash
from gitzen.zen_token import ZenToken


class GitPatch:
    zen_token: ZenToken
    hash: CommitHash

    def __init__(
        self,
        zen_token: ZenToken,
        hash: CommitHash,
    ) -> None:
        self.zen_token = zen_token
        self.hash = hash

    def __eq__(self, __o: object) -> bool:
        return (
            isinstance(__o, GitPatch)
            and self.zen_token == __o.zen_token
            and self.hash == __o.hash
        )

    def __repr__(self) -> str:
        return f"GitPatch(zen_token={self.zen_token}, hash={self.hash})"
