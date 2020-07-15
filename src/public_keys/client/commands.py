import getpass
import os
from pathlib import Path
from typing import Optional, Type

from public_keys.keyring.core import Keyring
from public_keys.keyring.file_system_for_testing import InMemoryTestingRing

from ..client.core import Client, PosixClient

DEFAULT_DIR = ".pks"
DEFAULT_CLIENT_STORE = "client"

try:
    type(raw_input)  # type: ignore
except NameError:
    raw_input = input


def get_name() -> str:
    return os.uname().nodename


def get_keyring() -> Type[Keyring]:
    return InMemoryTestingRing


def bootstrap(client_loc: Optional[os.PathLike] = None, sigchain_loc: Optional[str] = None) -> Client:
    if os.name == "posix":
        client = PosixClient()
        if client_loc is None:
            client_loc = Path.home()
            file_loc = client_loc / DEFAULT_DIR / DEFAULT_CLIENT_STORE
        else:
            client_loc = Path(client_loc)
            file_loc = client_loc / DEFAULT_CLIENT_STORE

        pwd = getpass.getpass("Enter Password:")

        try:
            with open(file_loc, "br") as bf:
                client._load(pwd, bf)
                client.keyring = get_keyring()()
        except FileNotFoundError:
            name = get_name()
            client.generate(name, get_keyring(), sigchain_loc)
            Path(client_loc / DEFAULT_DIR).mkdir(exist_ok=True)
            with open(file_loc, "bw") as bf:
                client._store(pwd, bf)

        return client
    else:
        raise Exception("Only currently implemented on POSIX")  # pragma: no cover
