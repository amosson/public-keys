from typing import Generator, Iterable, Protocol


class Store(Protocol):
    def loader(self) -> Generator[str, None, None]:
        ...

    def storer(self, raw_chain: Iterable[str]) -> None:
        ...

    def adder(self, entry: str) -> None:
        ...


class FileStore:
    def __init__(self, location: str):
        self.location = location

    def loader(self) -> Generator[str, None, None]:
        with open(self.location, "r") as f:
            for line in f:
                yield line[:-1]

    def storer(self, raw_chain: Iterable[str]) -> None:
        with open(self.location, "w") as f:
            for entry in raw_chain:
                f.write(entry)
                f.write("\n")

    def adder(self, entry: str) -> None:
        with open(self.location, "a") as f:
            f.write(entry)
            f.write("\n")


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
