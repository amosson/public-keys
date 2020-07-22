from pathlib import Path
from tempfile import TemporaryDirectory

from saltpack.encrypt import decrypt, encrypt  # type: ignore

from public_keys.client.commands import bootstrap
from public_keys.keyring.core import KeyKind
from public_keys.keyring.file_system_for_testing import InMemoryTestingRing


def mock_getpass(p=None, stream=None) -> str:
    return "password"


def mock_getpass_bad(p=None, stream=None) -> str:
    return "notthepassword"


class MockUnameInfo:
    nodename = "Node Name"


def mock_os_uname():
    return MockUnameInfo


def mock_in_memory_keyring():
    return InMemoryTestingRing


def test_encrypt_decrypt(monkeypatch) -> None:
    message = "This is a message to encrypt (and Decrypt)"
    monkeypatch.setattr("getpass.getpass", mock_getpass)
    monkeypatch.setattr("os.uname", mock_os_uname)
    with TemporaryDirectory() as home:
        monkeypatch.setattr(Path, "home", lambda: Path(home))
        c = bootstrap()

        assert c.keyring is not None
        eks = c.keyring.get(KeyKind.DEVICE_ENCRYPTION)
        assert eks is not None
        ek = eks[-1]

        spm = encrypt(ek.priv, [ek.pub], message.encode("utf-8"), 10 ** 6)
        assert spm is not None

        unencrypted_message = decrypt(spm, ek.priv)
        assert unencrypted_message.decode("utf-8") == message
