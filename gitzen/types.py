class ZenToken:
    _value: str

    @property
    def value(self) -> str:
        return self._value

    def __init__(self, value: str) -> None:
        self._value = value

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, ZenToken) and self._value == __o._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __repr__(self) -> str:
        return f"ZenToken({self._value})"


class GitHash:
    _value: str

    @property
    def value(self) -> str:
        return self._value

    def __init__(self, value: str) -> None:
        self._value = value

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, GitHash) and self._value == __o._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __repr__(self) -> str:
        return f"Hash({self._value})"
