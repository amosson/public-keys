import base64
import hashlib
import json

import nacl  # type: ignore
from nacl.signing import SigningKey, VerifyKey  # type: ignore

from public_keys.sigchain.core import (AddDevice, Authority, Entry, SigChain,
                                       create_device_and_add_to_chain,
                                       sign_kid_and_add_to_chain)
from public_keys.sigchain.stores import MemoryStore


def test_manual_validation_add_device(initial_add_device) -> None:
    decoded_entry = base64.b64decode(initial_add_device)
    sig_bytes = decoded_entry[0:64]
    message_bytes = decoded_entry[64:]
    message = json.loads(message_bytes.decode("utf-8"))

    vk = VerifyKey(message["authority"]["kid"], nacl.encoding.HexEncoder)
    assert vk.verify(message_bytes, sig_bytes)


def test_SigChainBasic() -> None:
    sc = SigChain(MemoryStore())
    assert len(sc) == 0


def test_one_device() -> None:
    ms = MemoryStore()
    sc = SigChain(ms)

    key = create_device_and_add_to_chain(sc, "name 1", "account 1", "test type 1")
    assert sc.is_valid()
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


def test_devices_two() -> None:
    ms = MemoryStore()
    sc = SigChain(ms)

    key1 = create_device_and_add_to_chain(sc, "name 1", "account 1", "test type 1")
    if key1 is not None:
        kid1 = key1.verify_key.encode().hex()
    key2 = create_device_and_add_to_chain(sc, "name 2", "account 1", "test type 1")
    if key2 is not None:
        kid2 = key2.verify_key.encode().hex()
    d1 = sc.devices[kid1]
    d2 = sc.devices[kid2]

    assert sc.is_valid()
    assert len(sc) == 2
    assert len(sc.devices) == 2
    assert d1.name == "name 1"
    assert d2.name == "name 2"

    assert sc.data_chain[0]["statement"]["name"] == "name 1"
    assert sc.data_chain[1]["statement"]["name"] == "name 2"

    sc = SigChain(ms)
    assert len(sc) == 0
    sc.load()

    assert len(sc) == 2
    assert len(sc.devices) == 2
    assert d1.name == "name 1"
    assert d2.name == "name 2"

    assert sc.data_chain[0]["statement"]["name"] == "name 1"
    assert sc.data_chain[1]["statement"]["name"] == "name 2"


def test_prev_hash_matches_hash_of_last_entry() -> None:
    ms = MemoryStore()
    sc = SigChain(ms)

    key = create_device_and_add_to_chain(sc, "name 1", "account 1", "test type 1")
    assert key

    assert hashlib.sha256(bytes(sc.raw_chain[0], "utf-8")).hexdigest() == sc.prev_hash


def test_sign_device() -> None:
    ms = MemoryStore()
    sc = SigChain(ms)

    key1 = create_device_and_add_to_chain(sc, "name 1", "account 1", "test type 1")
    kid1 = key1.verify_key.encode().hex()
    key2 = create_device_and_add_to_chain(sc, "name 2", "account 1", "test type 1")
    kid2 = key2.verify_key.encode().hex()
    d1 = sc.devices[kid1]
    d2 = sc.devices[kid2]

    assert sc.is_valid()
    assert len(sc) == 2
    assert len(sc.devices) == 2
    assert d1.name == "name 1"
    assert d2.name == "name 2"

    assert sc.data_chain[0]["statement"]["name"] == "name 1"
    assert sc.data_chain[1]["statement"]["name"] == "name 2"

    sign_kid_and_add_to_chain(sc, d2.signing_kid, key1, "account 1")
    assert len(sc) == 3
    assert d2.signed_by_kid == d1.signing_kid

    sc = SigChain(ms)
    assert len(sc) == 0
    sc.load()

    assert sc.is_valid()
    assert len(sc) == 3
    d1 = sc.devices[kid1]
    d2 = sc.devices[kid2]
    assert d2.signed_by_kid == d1.signing_kid


def test_manual_create_entry_has_initial_hash() -> None:
    sk = SigningKey.generate()
    a = Authority("test", sk)
    d = AddDevice("test", "test kind", "123", sk)

    e = Entry(d, a, 0)
    assert e.prev == bytearray(32).hex()
