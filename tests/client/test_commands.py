from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from nacl.exceptions import CryptoError  # type: ignore # noqa: I100

from public_keys.client import commands
from public_keys.client.commands import bootstrap, get_keyring
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


def test_bootstrap(monkeypatch) -> None:
    monkeypatch.setattr("getpass.getpass", mock_getpass)
    monkeypatch.setattr("os.uname", mock_os_uname)
    with TemporaryDirectory() as home:
        monkeypatch.setattr(Path, "home", lambda: Path(home))
        c = bootstrap()
        assert c is not None
        assert c.id is not None
        assert c.name == "Node Name"
        assert len(c.id) == 64
        assert c.sigchain is None

        loaded = bootstrap()
        assert c.id == loaded.id
        assert c.name == loaded.name
        assert c.sigchain == loaded.sigchain


def test_bootstrap_bad_password_on_load(monkeypatch) -> None:
    monkeypatch.setattr("getpass.getpass", mock_getpass)
    monkeypatch.setattr("os.uname", mock_os_uname)
    with TemporaryDirectory() as home:
        monkeypatch.setattr(Path, "home", lambda: Path(home))
        c = bootstrap()
        assert c is not None
        assert c.id is not None
        assert c.name == "Node Name"
        assert len(c.id) == 64

        monkeypatch.setattr("getpass.getpass", mock_getpass_bad)
        with pytest.raises(CryptoError):
            loaded = bootstrap()
            assert loaded is None


def test_bootstrap_directory_exists(monkeypatch) -> None:
    monkeypatch.setattr("getpass.getpass", mock_getpass)
    monkeypatch.setattr("os.uname", mock_os_uname)

    with TemporaryDirectory() as home:
        monkeypatch.setattr(Path, "home", lambda: Path(home))
        (Path(home) / ".pks").mkdir()
        c = bootstrap()
        assert c is not None
        assert c.id is not None
        assert c.name == "Node Name"
        assert len(c.id) == 64

        loaded = bootstrap()
        assert c.id == loaded.id
        assert c.name == loaded.name


def test_bootstrap_specify_directory(monkeypatch) -> None:
    monkeypatch.setattr("getpass.getpass", mock_getpass)
    monkeypatch.setattr("os.uname", mock_os_uname)

    with TemporaryDirectory() as home:
        monkeypatch.setattr(Path, "home", lambda: Path(home))
        loc = Path(home) / "somethingselse"
        loc.mkdir()

        c = bootstrap(loc)
        assert c is not None
        assert c.id is not None
        assert c.name == "Node Name"
        assert len(c.id) == 64

        loaded = bootstrap(loc)
        assert c.id == loaded.id
        assert c.name == loaded.name

        loaded_wrong_loc = bootstrap()
        assert c.id != loaded_wrong_loc.id
        assert c.name == loaded_wrong_loc.name


def test_keyring_save(monkeypatch) -> None:
    monkeypatch.setattr("getpass.getpass", mock_getpass)
    monkeypatch.setattr("os.uname", mock_os_uname)
    monkeypatch.setattr(commands, "get_keyring", mock_in_memory_keyring)

    with TemporaryDirectory() as home:
        monkeypatch.setattr(Path, "home", lambda: Path(home))
        c = bootstrap()
        kr = c.keyring
        if kr is not None:
            assert len(kr) == 2
        else:
            assert 1 == 0


def test_associate_sigchain_file(monkeypatch) -> None:
    monkeypatch.setattr("getpass.getpass", mock_getpass)
    monkeypatch.setattr("os.uname", mock_os_uname)
    monkeypatch.setattr(commands, "get_keyring", mock_in_memory_keyring)

    with TemporaryDirectory() as home:
        monkeypatch.setattr(Path, "home", lambda: Path(home))
        sigchain_loc = str(Path.home() / "sigchain") + "@localhost"
        c = bootstrap(sigchain_loc=sigchain_loc)
        assert c.id is not None

        assert c.sigchain is not None
        assert c.keyring is not None
        assert len(c.sigchain) == 1
        assert len(c.sigchain.devices) == 1
        d = list(c.sigchain.devices.values())[0]
        assert d.device_id == c.id
        sk = c.keyring.get(KeyKind.DEVICE_SIGNING)
        assert sk is not None


def test_get_keyring_keeps_saved_keys():  # Not going to type check simply dict entries
    a = get_keyring()()
    a[1] = 2
    assert a[1] == 2

    b = get_keyring()()
    assert b[1] == 2
    b[1] = 3
    assert a[1] == 3


def test_associate_sigchain_file_can_load_after_store(monkeypatch) -> None:
    monkeypatch.setattr("getpass.getpass", mock_getpass)
    monkeypatch.setattr("os.uname", mock_os_uname)
    # monkeypatch.setattr(commands, "get_keyring", mock_in_memory_keyring)

    with TemporaryDirectory() as home:
        assert Path(home).exists()
        monkeypatch.setattr(Path, "home", lambda: Path(home))
        sigchain_loc = str(Path.home() / "sigchain") + "@localhost"
        c = bootstrap(sigchain_loc=sigchain_loc)
        assert c.id is not None
        assert c.sigchain is not None
        assert len(c.sigchain) == 1
        assert c.sigchain.store.location() == sigchain_loc
        assert (Path.home() / "sigchain").exists()
        assert c.keyring is not None
        sk = c.keyring.get(KeyKind.DEVICE_SIGNING)
        assert sk is not None

        # import pdb

        # pdb.set_trace()
        loaded = bootstrap()
        assert loaded.keyring is not None
        sk = loaded.keyring.get(KeyKind.DEVICE_SIGNING)
        assert sk is not None
        assert loaded.id == c.id
        assert loaded.sigchain is not None

        assert len(loaded.sigchain) == 1
        assert len(loaded.sigchain.devices) == 1
        d = list(loaded.sigchain.devices.values())[0]
        assert d.device_id == loaded.id
        assert loaded.keyring is not None
        sk = loaded.keyring.get(KeyKind.DEVICE_SIGNING)
        assert sk is not None
