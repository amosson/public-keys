import os
from tempfile import NamedTemporaryFile

import pytest

from public_keys.sigchain.stores import FileStore, MemoryStore, create_store


def test_MemoryStore_adder() -> None:
    ms = MemoryStore()

    ms.adder("an entry")
    assert len(ms.entries) == 1
    assert ms.entries[0] == "an entry"


def test_MemoryStore_storer() -> None:
    ms = MemoryStore()
    rc = ["a", "b", "c"]

    ms.storer(rc)

    assert ms.entries[0] == "a"
    assert ms.entries[1] == "b"
    assert ms.entries[2] == "c"


def test_FileStore_storer() -> None:
    tf = NamedTemporaryFile(delete=False)

    fs = FileStore(tf.name)
    rc = ["a", "b"]

    fs.storer(rc)

    f = open(tf.name, "r")
    assert f.read() == "a\nb\n"

    os.unlink(tf.name)


def test_FileStore_adder() -> None:
    tf = NamedTemporaryFile(delete=False)

    fs = FileStore(tf.name)
    fs.adder("an entry")

    f = open(tf.name, "r")
    assert f.read() == "an entry\n"

    os.unlink(tf.name)


def test_FileStore_load() -> None:
    tf = NamedTemporaryFile("w", delete=False)
    tf.write("a\nb\n")
    tf.close()

    fs = FileStore(tf.name)
    out = []
    for e in fs.loader():
        out.append(e)

    assert out[0] == "a"
    assert out[1] == "b"

    os.unlink(tf.name)


def test_create_store_empty_in_memory() -> None:
    ms = create_store("@inmemory")
    if isinstance(ms, MemoryStore):
        assert len(ms.entries) == 0
    else:
        assert 1 == 0


def test_create_store_in_memory() -> None:
    entries = ["a", "b"]

    ms = create_store("@inmemory", entries)
    assert ms.location() == "@inmemory"
    if isinstance(ms, MemoryStore):
        assert len(ms.entries) == 2
        assert ms.entries[0] == "a"
        assert ms.entries[1] == "b"
    else:
        assert 1 == 0


def test_create_store_file_store() -> None:
    tf = NamedTemporaryFile(delete=False)

    fs = FileStore(tf.name)
    fs.adder("an entry")

    out = create_store(fs.location())
    entries = []
    for e in out.loader():
        entries.append(e)
    assert len(entries) == 1
    assert entries[0] == "an entry"


def test_create_store_unknown_type() -> None:
    with pytest.raises(Exception) as ex:
        s = create_store("@unknown")
        assert s is None

    assert str(ex.value).startswith("Unsupported")
