from sigchain.core import SigChain, create_device_and_add_to_chain
from sigchain.stores import MemoryStore

from nacl.signing import SigningKey


def test_SigChainBasic() -> None:
    sc = SigChain(MemoryStore())
    assert len(sc) == 0


def test_one_device() -> None:
    ms = MemoryStore()
    sc = SigChain(ms)

    key = create_device_and_add_to_chain(sc, "name 1", "account 1", "test type 1")
    assert key is not None
    assert len(sc) == 1
    assert len(sc.devices) == 1
    assert len(sc.data_chain) == 1
    assert len(sc.raw_chain) == 1
    kid = key.verify_key.encode().hex()
    d = sc.devices[kid]
    assert d.name == "name 1"
    assert d.kind == "test type 1"

    assert len(ms.entries) == 1

    sc = SigChain(ms)
    assert len(sc) == 0
    sc.load()
    assert sc.is_valid()
    assert len(sc) == 1
    assert len(sc.devices) == 1
    assert len(sc.data_chain) == 1
    assert len(sc.raw_chain) == 1
    kid = key.verify_key.encode().hex()
    d = sc.devices[kid]
    assert d.name == "name 1"
    assert d.kind == "test type 1"
