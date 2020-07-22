# from pathlib import Path
# from tempfile import TemporaryDirectory

# import pytest
# from nacl.exceptions import CryptoError  # type: ignore # noqa: I100

# from public_keys.client import commands
# from public_keys.client.commands import bootstrap, get_keyring
# from public_keys.keyring.core import KeyKind
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
