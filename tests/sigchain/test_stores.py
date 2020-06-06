from sigchain.stores import MemoryStore


def test_MemoryStore_adder() -> None:
    ms = MemoryStore()

    ms.adder("an entry")
    assert len(ms.entries) == 1
    assert ms.entries[0] == "an entry"
