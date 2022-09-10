from typing import Optional

from gitzen.types import ZenToken


class Commit:
    zen_token: Optional[ZenToken]
    hash: str
    messageHeadline: str
    messageBody: str
    wip: bool

    def __init__(
        self,
        zen_token: Optional[ZenToken],
        hash: str,
        headline: str,
        body: str,
        wip: bool,
    ) -> None:
        self.zen_token = zen_token
        self.hash = hash
        self.messageHeadline = headline
        self.messageBody = body
        self.wip = wip

    def __eq__(self, __o: object) -> bool:
        return (
            isinstance(__o, Commit)
            and self.zen_token == __o.zen_token
            and self.hash == __o.hash
            and self.messageHeadline == __o.messageHeadline
            and self.messageBody == __o.messageBody
            and self.wip == __o.wip
        )

    def __repr__(self) -> str:
        return (
            f"Commit(zen_token={self.zen_token}, "
            f"hash={self.hash}, "
            f"messageHeadline={self.messageHeadline}, "
            f"messageBody={self.messageBody}, "
            f"wip={repr(self.wip)})"
        )
