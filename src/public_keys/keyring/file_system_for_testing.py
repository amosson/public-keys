from typing import Iterator, List, MutableMapping, Optional

from public_keys.keyring.core import Key, KeyKind, Keyring


class InMemoryTestingRing(Keyring):
    def __init__(self, d: Optional[MutableMapping[KeyKind, List[Key]]] = None) -> None:
        if d is None:
            d = {}
        self.dict = d

    def lock(self, password: str) -> None:
        pass

    def unlock(self, password: str, count: int) -> None:
        pass

    def __getitem__(self, k: KeyKind) -> List[Key]:
        return self.dict[k]

    def __setitem__(self, k: KeyKind, v: List[Key]) -> None:
        self.dict[k] = v

    def __delitem__(self, k: KeyKind) -> None:
        del self.dict[k]

    def __iter__(self) -> Iterator[KeyKind]:
        return self.dict.__iter__()

    def __len__(self) -> int:
        return len(self.dict)
