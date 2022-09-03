class Commit:
    hash_id: str
    messageHeadline: str
    messageBody: str
    status: str  # enum

    def __init__(self, hash_id: str, headline: str, body: str, status: str):
        self.hash_id = hash_id
        self.messageHeadline = headline
        self.messageBody = body
        self.status = status

    def __eq__(self, __o: object) -> bool:
        return (
            self.hash_id == __o.hash_id
            and self.messageHeadline == __o.messageHeadline
            and self.messageBody == __o.messageBody
            and self.status == __o.status
        )

    def __repr__(self) -> str:
        return (
            f"Commit(hash_id={repr(self.hash_id)}, "
            f"messageHeadline={repr(self.messageHeadline)}, "
            f"messageBody={repr(self.messageBody)}, "
            f"status={repr(self.status)})"
        )
