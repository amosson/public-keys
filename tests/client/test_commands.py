from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from nacl.exceptions import CryptoError  # type: ignore # noqa: I100

from public_keys.client import commands
from public_keys.client.commands import bootstrap
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

        loaded = bootstrap()
        assert c.id == loaded.id
        assert c.name == loaded.name


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
