class Commit:
    oid: str
    messageHeadline: str
    messageBody: str
    status: str  # enum

    def __init__(self, oid: str, headline: str, body: str, status: str):
        self.oid = oid
        self.messageHeadline = headline
        self.messageBody = body
        self.status = status

    def __eq__(self, __o: object) -> bool:
        return (
            self.oid == __o.oid
            and self.messageHeadline == __o.messageHeadline
            and self.messageBody == __o.messageBody
            and self.status == __o.status
        )

    def __repr__(self) -> str:
        return (
            f"Commit(oid={repr(self.oid)}, "
            f"messageHeadline={repr(self.messageHeadline)}, "
            f"messageBody={repr(self.messageBody)}, "
            f"status={repr(self.status)})"
        )
