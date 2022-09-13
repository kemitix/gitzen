from typing import List


def write(filename: str, contents: List[str]) -> None:
    with open(filename, "w") as f:
        f.write("\n".join(contents))


def read(filename: str) -> List[str]:
    with open(filename, "r") as f:
        return f.read().splitlines()
