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
from public_keys.sigchain.core import (SigChain,
                                       create_device_and_add_to_chain,
                                       sign_kid_and_add_to_chain)
from public_keys.sigchain.stores import create_store

DEVICE_SIG = b"Derived-Device-NaCl-EdDSA-1"
DEVICE_DH = b"Derived-User-NaCl-DH-1"


class Client:
    __slots__ = ["id", "name", "keyring", "sigchain"]

    def __init__(self) -> None:
        self.id: Optional[str] = None
        self.name: Optional[str] = None
        self.keyring: Optional[Keyring] = None
        self.sigchain: Optional[SigChain] = None

    def generate(self, name: str, keyring_cls: Type[Keyring], sigchain_loc: Optional[str] = None) -> None:
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

        if sigchain_loc is not None:
            self.associate_sigchain(sigchain_loc)

    def associate_sigchain(self, sigchain_loc: str) -> None:
        if self.keyring is None:
            raise Exception("Trying to associate a sigchain to a client with no keyring")
        else:
            sks = self.keyring[KeyKind.DEVICE_SIGNING]
            if sks is not None and len(sks):
                sk = SigningKey(sks[-1].priv)
            else:
                raise Exception("Trying to associate a sigchain to a client with no DEVICE SIGNING KEY")
            eks = self.keyring[KeyKind.DEVICE_ENCRYPTION]
            if eks is not None and len(eks):
                pub_ek = eks[-1].pub.hex()
            else:
                raise Exception("Trying to associate a sigchain to a client with no DEVICE ENCRYPTION KEY")

        if self.sigchain is not None:
            raise Exception("Client already has a sigchain - can't associate a new one")
        else:
            self.sigchain = SigChain(create_store(sigchain_loc))

            if self.name is not None and self.id is not None:
                create_device_and_add_to_chain(self.sigchain, self.name, sigchain_loc, "DEVICE_SIG", sk, self.id)
                sign_kid_and_add_to_chain(self.sigchain, pub_ek, sk, sigchain_loc, KeyKind.DEVICE_ENCRYPTION, self.id)
            else:
                raise Exception("Trying to associate a sigchain to a client with no name or no id")

    def _store(self, password: str, openfile: BinaryIO) -> None:
        if self.sigchain is None:
            sigchain_loc = None
        else:
            sigchain_loc = self.sigchain.store.location()
        d = {"id": self.id, "name": self.name, "sigchain.location": sigchain_loc}
        salt = random(SALTBYTES)
        sb = SecretBox(kdf(SecretBox.KEY_SIZE, bytes(password, "utf-8"), salt, memlimit=MEMLIMIT_INTERACTIVE))
        openfile.write(salt)
        openfile.write(sb.encrypt(bytes(json.dumps(d), "utf-8")))
        if self.keyring is not None:
            self.keyring.lock(password)
        else:
            pass  # pragma: nocover

    def _load(self, password: str, openfile: BinaryIO) -> None:
        salt = openfile.read(SALTBYTES)
        data = openfile.read()
        sb = SecretBox(kdf(SecretBox.KEY_SIZE, bytes(password, "utf-8"), salt, memlimit=MEMLIMIT_INTERACTIVE))
        d = json.loads(sb.decrypt(data).decode("utf-8"))
        self.id = d["id"]
        self.name = d["name"]
        sigchain_loc = d["sigchain.location"]
        if sigchain_loc is not None:
            self.sigchain = SigChain(create_store(sigchain_loc))
            self.sigchain.load()


class PosixClient(Client):
    __slots__ = ["client_loc", "keyring_type"]

    def __init__(self) -> None:
        super().__init__()
        self.client_loc: Optional[str] = None
        self.keyring_type: Optional[str] = None
