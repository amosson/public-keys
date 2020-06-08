from public_keys.keyring.file_system_for_testing import InMemoryTestingRing


def test_InMemoryTestingRing() -> None:
    a = InMemoryTestingRing()
    a.lock("a")
    a.unlock("a", 1)
    a["a"] = "b"
    assert a["a"] == "b"
    a["a"] = "c"
    assert a["a"] == "c"
