import pytest
from nacl.utils import random  # type: ignore # noqa: I100

from public_keys.client.core import Client
from public_keys.keyring.core import Key, KeyKind
from public_keys.keyring.file_system_for_testing import InMemoryTestingRing
from public_keys.sigchain.core import SigChain
from public_keys.sigchain.stores import create_store


def test_associate_sigchain_no_keyring() -> None:
    c = Client()
    with pytest.raises(Exception) as ex:
        c.associate_sigchain("hello")

    assert str(ex.value).endswith("no keyring")


def test_associate_sigchain_no_device_signing() -> None:
    c = Client()
    c.keyring = InMemoryTestingRing()

    with pytest.raises(Exception):
        c.associate_sigchain("hello")

    c.keyring[KeyKind.DEVICE_SIGNING] = []
    with pytest.raises(Exception) as ex:
        c.associate_sigchain("hello")
    assert str(ex.value).endswith("no DEVICE SIGNING KEY")


def test_associate_signchain_existing_sigchain() -> None:
    c = Client()
    k = Key(KeyKind.DEVICE_SIGNING, random(), random())
    c.keyring = InMemoryTestingRing()
    c.keyring[KeyKind.DEVICE_SIGNING] = [k]

    c.sigchain = SigChain(create_store("@inmemory"))

    with pytest.raises(Exception) as ex:
        c.associate_sigchain("hello")
    assert str(ex.value).endswith("associate a new one")


def test_associate_sigchain_no_name() -> None:
    c = Client()
    k = Key(KeyKind.DEVICE_SIGNING, random(), random())
    c.keyring = InMemoryTestingRing()
    c.keyring[KeyKind.DEVICE_SIGNING] = [k]

    with pytest.raises(Exception) as ex:
        c.associate_sigchain("@inmemory")
    assert str(ex.value).endswith("no name or no id")
