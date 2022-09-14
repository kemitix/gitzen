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


class BoolWrapper:
    _value: bool
    _type: type

    @property
    def value(self) -> bool:
        return self._value

    def __init__(self, type: type, value: bool) -> None:
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


class PullRequestId(StrWrapper):
    def __init__(self, value: str) -> None:
        super().__init__(PullRequestId, value)


class PullRequestNumber(StrWrapper):
    def __init__(self, value: str) -> None:
        super().__init__(PullRequestNumber, value)


class PullRequestTitle(StrWrapper):
    def __init__(self, value: str) -> None:
        super().__init__(PullRequestTitle, value)


class GithubRepoId(StrWrapper):
    def __init__(self, value: str) -> None:
        super().__init__(GithubRepoId, value)


class PullRequestMergeable(StrWrapper):
    def __init__(self, value: str) -> None:
        super().__init__(PullRequestMergeable, value)


class PullRequestReviewDecision(StrWrapper):
    def __init__(self, value: str) -> None:
        super().__init__(PullRequestReviewDecision, value)


class GithubUsername(StrWrapper):
    def __init__(self, value: str) -> None:
        super().__init__(GithubUsername, value)


class GitBranchName(StrWrapper):
    def __init__(self, value: str) -> None:
        super().__init__(GitBranchName, value)


class GitRemoteName(StrWrapper):
    def __init__(self, value: str) -> None:
        super().__init__(GitRemoteName, value)


class GitRootDir(StrWrapper):
    def __init__(self, value: str) -> None:
        super().__init__(GitRootDir, value)


class CommitWipStatus(BoolWrapper):
    def __init__(self, value: bool) -> None:
        super().__init__(CommitWipStatus, value)
