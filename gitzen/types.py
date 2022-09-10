class StrWrapper:
    _value: str
    _type: type

    @property
    def value(self) -> str:
        return self._value

    def __init__(self, type: type, value: str) -> None:
        self._type = type
        self._value = value

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, self._type) and self._value == __o._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __repr__(self) -> str:
        return f"{self._type.__name__}({self._value})"


class ZenToken(StrWrapper):
    def __init__(self, value: str) -> None:
        super().__init__(ZenToken, value)


class CommitHash(StrWrapper):
    def __init__(self, value: str) -> None:
        super().__init__(CommitHash, value)


class CommitTitle(StrWrapper):
    def __init__(self, value: str) -> None:
        super().__init__(CommitTitle, value)


class CommitBody(StrWrapper):
    def __init__(self, value: str) -> None:
        super().__init__(CommitBody, value)


class PullRequestBody(StrWrapper):
    def __init__(self, value: str) -> None:
        super().__init__(PullRequestBody, value)
