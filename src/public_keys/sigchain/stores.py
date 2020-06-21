from typing import Generator, Iterable, Optional, Protocol


class Store(Protocol):
    def loader(self) -> Generator[str, None, None]:
        ...  # pragma: no cover

    def storer(self, raw_chain: Iterable[str]) -> None:
        ...  # pragma: no cover

    def adder(self, entry: str) -> None:
        ...  # pragma: no cover

    def location(self) -> str:
        ...  # pragma: no cover


class FileStore:
    def __init__(self, location: str):
        self.loc = location

    def loader(self) -> Generator[str, None, None]:
        with open(self.loc, "r") as f:
            for line in f:
                yield line[:-1]

    def storer(self, raw_chain: Iterable[str]) -> None:
        with open(self.loc, "w") as f:
            for entry in raw_chain:
                f.write(entry)
                f.write("\n")

    def adder(self, entry: str) -> None:
        with open(self.loc, "a") as f:
            f.write(entry)
            f.write("\n")

    def location(self) -> str:
        return self.loc + "@localhost"


class MemoryStore:
    def __init__(self):
        self.entries = []

    def loader(self) -> Generator[str, None, None]:
        for entry in self.entries:
            yield entry

    def storer(self, raw_chain: Iterable[str]) -> None:
        for entry in raw_chain:
            self.entries.append(entry)

    def adder(self, entry: str) -> None:
        self.entries.append(entry)

    def location(self) -> str:
        return "@inmemory"


def create_store(loc: str, entities: Optional[Iterable[str]] = None) -> Store:
    if loc.endswith("@localhost"):
        return FileStore(loc[:-10])
    if loc == "@inmemory":
        ms = MemoryStore()
        if entities is not None:
            ms.storer(entities)
        return ms

    raise Exception("Unsupported Store Type: %s" % loc)
