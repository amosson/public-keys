import hmac
import json
from hashlib import sha256
from typing import BinaryIO, Optional, Type

from nacl.public import PrivateKey  # type: ignore
from nacl.pwhash.argon2i import MEMLIMIT_INTERACTIVE  # type: ignore
from nacl.pwhash.argon2i import SALTBYTES, kdf
from nacl.secret import SecretBox  # type: ignore
from nacl.signing import SigningKey  # type: ignore
from nacl.utils import random  # type: ignore

from public_keys.keyring.core import Key, KeyKind, Keyring
from public_keys.sigchain.core import SigChain

DEVICE_SIG = b"Derived-Device-NaCl-EdDSA-1"
DEVICE_DH = b"Derived-User-NaCl-DH-1"


class Client:
    __slots__ = ["id", "name", "keyring", "sigchain"]

    def __init__(self) -> None:
        self.id: Optional[str] = None
        self.name: Optional[str] = None
        self.keyring: Optional[Keyring] = None
        self.sigchain: Optional[SigChain] = None

    def generate(self, name: str, keyring_cls: Type[Keyring]) -> None:
        self.id = random().hex()
        self.name = name

        seed = random()
        signing_seed = hmac.new(seed, DEVICE_SIG, sha256).digest()
        dh_seed = hmac.new(seed, DEVICE_DH, sha256).digest()
        signing_key = SigningKey(signing_seed)
        dh_key = PrivateKey.from_seed(dh_seed)

        d = {
            KeyKind.DEVICE_SIGNING: [
                Key(KeyKind.DEVICE_SIGNING, signing_key.encode(), signing_key.verify_key.encode())
            ],
            KeyKind.DEVICE_ENCRYPTION: [Key(KeyKind.DEVICE_ENCRYPTION, dh_key.encode(), dh_key.public_key.encode())],
        }

        self.keyring = keyring_cls(d)

    def _store(self, password: str, openfile: BinaryIO) -> None:
        d = {"id": self.id, "name": self.name}
        salt = random(SALTBYTES)
        sb = SecretBox(kdf(SecretBox.KEY_SIZE, bytes(password, "utf-8"), salt, memlimit=MEMLIMIT_INTERACTIVE))
        openfile.write(salt)
        openfile.write(sb.encrypt(bytes(json.dumps(d), "utf-8")))

    def _load(self, password: str, openfile: BinaryIO) -> None:
        salt = openfile.read(SALTBYTES)
        data = openfile.read()
        sb = SecretBox(kdf(SecretBox.KEY_SIZE, bytes(password, "utf-8"), salt, memlimit=MEMLIMIT_INTERACTIVE))
        d = json.loads(sb.decrypt(data).decode("utf-8"))
        self.id = d["id"]
        self.name = d["name"]


class PosixClient(Client):
    __slots__ = ["client_loc", "keyring_type"]

    def __init__(self) -> None:
        super().__init__()
        self.client_loc: Optional[str] = None
        self.keyring_type: Optional[str] = None
