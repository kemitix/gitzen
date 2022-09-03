class Commit:
    zen_token: str
    hash: str
    messageHeadline: str
    messageBody: str

    def __init__(
        self,
        zen_token: str,
        hash: str,
        headline: str,
        body: str,
    ):
        self.zen_token = zen_token
        self.hash = hash
        self.messageHeadline = headline
        self.messageBody = body

    def __eq__(self, __o: object) -> bool:
        return (
            self.zen_token == __o.zen_token
            and self.hash == __o.hash
            and self.messageHeadline == __o.messageHeadline
            and self.messageBody == __o.messageBody
        )

    def __repr__(self) -> str:
        return (
            f"Commit(zen_token={self.zen_token}, "
            f"hash={self.hash}, "
            f"messageHeadline={self.messageHeadline}, "
            f"messageBody={self.messageBody})"
        )
