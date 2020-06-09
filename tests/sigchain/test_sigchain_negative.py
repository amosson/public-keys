import base64
import json

import nacl  # type: ignore
from nacl.exceptions import BadSignatureError  # type: ignore
from nacl.signing import VerifyKey  # type: ignore
from pytest import fixture  # type: ignore

from public_keys.sigchain.core import SigChain
from public_keys.sigchain.stores import MemoryStore


@fixture
def bad_initial_hash() -> str:
    return (
        "YrPn8TRcPziGtxPeLPX1QXXkV+UjVAyAw/KfhR/VuUoobuqHzTW6NPiSO4q3FN23CgBEbj2TOqlQlj9OK+EIDXsic3RhdGVtZW50I"
        "jogeyJkZXZpY2VfaWQiOiAiIiwgImtpbmQiOiAidGVzdCIsICJuYW1lIjogInRlc3QgZm9yIGJhZCBzaWduYXR1cmUiLCAia2lkIj"
        "ogIjkxMWNmZjVmOTFiZjU2NWQ3YzAxZDJlMDNlNTc5YTc1N2VjNGU4N2IxNTRjMzRmOWYwOWE3ZDllOTJiYzMzZTYiLCAic3RhdGV"
        "tZW50X3R5cGUiOiAic2VsZi1zaWduZWQtZGV2aWNlIn0sICJhdXRob3JpdHkiOiB7ImtpZCI6ICI5MTFjZmY1ZjkxYmY1NjVkN2Mw"
        "MWQyZTAzZTU3OWE3NTdlYzRlODdiMTU0YzM0ZjlmMDlhN2Q5ZTkyYmMzM2U2IiwgInVzZXJuYW1lIjogInRlc3QifSwgInByZXYiO"
        "iAiMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMSIsICJzZXEiOiAwfQ=="
    )


def test_manual_validation_add_device(initial_add_device) -> None:
    e_list = list(initial_add_device)
    e_list[5] = "1"

    decoded_entry = base64.b64decode("".join(e_list))
    sig_bytes = decoded_entry[0:64]
    message_bytes = decoded_entry[64:]
    message = json.loads(message_bytes.decode("utf-8"))

    vk = VerifyKey(message["authority"]["kid"], nacl.encoding.HexEncoder)
    try:
        assert vk.verify(message_bytes, sig_bytes)
        assert 0  # Should throw an excpetion
    except BadSignatureError:
        pass


def test_sigchain_validation_bad_add_device(initial_add_device) -> None:
    e_list = list(initial_add_device)
    e_list[5] = "1"

    ms = MemoryStore()
    ms.entries.append("".join(e_list))
    sc = SigChain(ms)
    sc.load()

    assert not sc.is_valid()
    assert sc.error_reason == "Bad signature"


def test_sigchain_validation_bad_prev_initial_entry(bad_initial_hash) -> None:
    ms = MemoryStore()
    ms.entries.append(bad_initial_hash)
    sc = SigChain(ms)
    sc.load()

    assert not sc.is_valid()
    assert sc.error_reason == "Hash mismatch"


def test_sigchain_two_entries_bad_hash_on_second(initial_add_device, bad_initial_hash) -> None:
    ms = MemoryStore()
    ms.entries.append(initial_add_device)
    ms.entries.append(bad_initial_hash)

    sc = SigChain(ms)
    sc.load()

    assert not sc.is_valid()
    assert sc.error_reason == "Hash mismatch"
    assert len(sc) == 1  # Ensure failure is on second entry
