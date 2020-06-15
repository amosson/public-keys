from nacl.signing import SigningKey, VerifyKey  # type: ignore

from public_keys.client.core import Client
from public_keys.keyring.core import KeyKind
from public_keys.keyring.file_system_for_testing import InMemoryTestingRing


def test_init() -> None:
    c = Client()
    assert c.id is None
    assert c.keyring is None
    assert c.name is None
    assert c.sigchain is None


def test_generate() -> None:
    c = Client()
    c.generate("test client", InMemoryTestingRing)
    assert c.id is not None
    assert c.name == "test client"
    assert c.sigchain is None

    if c.keyring is not None:
        assert len(c.keyring) == 2
        # Sign Something
        raw_sk = c.keyring[KeyKind.DEVICE_SIGNING][0]
        sk = SigningKey(raw_sk.priv)
        signed = sk.sign(b"something")
        vk = VerifyKey(raw_sk.pub)

        assert vk.verify(signed)
    else:
        assert 1 == 0
