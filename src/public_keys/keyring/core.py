from typing import Mapping


class Keyring(Mapping[str, str]):
    def lock(self, password: str) -> None:
        ...  # pragma: no cover

    def unlock(self, password: str, count: int) -> None:
        ...  # pragma: no cover
