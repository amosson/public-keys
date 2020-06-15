from public_keys.keyring.core import Key, KeyKind
from public_keys.keyring.file_system_for_testing import InMemoryTestingRing


def test_InMemoryTestingRing() -> None:
    a = InMemoryTestingRing()
    a.lock("a")
    a.unlock("a", 1)
    a[KeyKind.UNKNOWN] = [Key(KeyKind.UNKNOWN, b"a", b"b")]
    assert a[KeyKind.UNKNOWN][0].pub == b"b"


def test_create_from_dict() -> None:
    d = {KeyKind.UNKNOWN: [Key(KeyKind.UNKNOWN, b"a", b"b")]}
    a = InMemoryTestingRing(d)
    assert len(a) == 1


def test_del() -> None:
    d = {KeyKind.UNKNOWN: [Key(KeyKind.UNKNOWN, b"a", b"b")]}
    a = InMemoryTestingRing(d)
    assert len(a) == 1

    del a[KeyKind.UNKNOWN]
    assert len(a) == 0


def test_iter() -> None:
    d = {KeyKind.UNKNOWN: [Key(KeyKind.UNKNOWN, b"a", b"b")]}
    a = InMemoryTestingRing(d)
    assert len(a) == 1

    for k in a:
        assert k == KeyKind.UNKNOWN
