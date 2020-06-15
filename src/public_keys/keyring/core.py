from enum import Enum
from typing import List, MutableMapping, Optional


class KeyKind(Enum):
    UNKNOWN = 0
    DEVICE_SIGNING = 1
    DEVICE_ENCRYPTION = 2
    DEVICE_SEED = 3
    PUK_SIGNING = 4
    PUK_ENCRYPTION = 5
    PUK_SEED = 6


class Key:
    __slots__ = ["kind", "priv", "pub"]

    def __init__(self, kind: KeyKind, priv: bytes, pub: bytes) -> None:
        self.kind = kind
        self.priv: Optional[bytes] = priv
        self.pub = pub


class Keyring(MutableMapping[KeyKind, List[Key]]):
    def __init__(self, d: MutableMapping[KeyKind, List[Key]]) -> None:
        ...  # pragma: no cover

    def lock(self, password: str) -> None:
        ...  # pragma: no cover

    def unlock(self, password: str, count: int) -> None:
        ...  # pragma: no cover

    def get_by_public_key(self, str) -> Key:
        ...  # pragma: no cover
