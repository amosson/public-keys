import base64
import hashlib
import json
from dataclasses import dataclass
from typing import List, Mapping, MutableMapping, Optional, Tuple

import nacl  # type: ignore
from nacl.exceptions import BadSignatureError  # type: ignore
from nacl.signing import SigningKey, VerifyKey  # type: ignore
from nacl.utils import random  # type: ignore

from public_keys.sigchain.stores import Store


class Authority:
    def __init__(self, username, signing_key):
        self.username = username
        self.signing_key = signing_key

    def as_dict(self):
        return {
            "kid": self.signing_key.verify_key.encode().hex(),
            "username": self.username,
        }

    def as_json(self):
        return json.dumps(self.as_dict())


class Statement:
    def as_json(self):
        return json.dumps(self.as_dict())

    def as_base64(self):
        return base64.b64encode(self.as_json())


@dataclass
class AddDevice(Statement):
    name: str
    kind: str
    device_id: str
    device_key: SigningKey
    statement_type: str = "self-signed-device"

    def as_dict(self):
        return {
            "device_id": self.device_id,
            "kind": self.kind,
            "name": self.name,
            "kid": self.device_key.verify_key.encode().hex(),
            "statement_type": self.statement_type,
        }


ADD_DEVICE_KEYS = set(["device_id", "kind", "name", "kid", "statement_type"])


@dataclass
class SignedKid(Statement):
    signer: SigningKey
    kid: str

    def as_dict(self):
        signed_key = self.signer.sign(bytes(self.kid, "utf-8")).signature.hex()
        return {
            "kid": self.kid,
            "signed_kid": signed_key,
        }


SIGNED_KID_KEYS = set(["kid", "signed_kid"])


@dataclass
class Device:
    device_id: str
    signing_kid: str
    name: str
    kind: str
    encryption_key: Optional[str] = None
    signed_by_kid: Optional[str] = None
    revoke_seq: Optional[int] = None


class SigChain:
    def __init__(self, store: Store) -> None:
        self.store = store
        self.raw_chain: List[str] = []
        self.data_chain: List[Mapping] = []
        self.error_entry: Optional[str] = None
        self.error_entry_as_dict: Optional[Mapping] = None
        self.error_reason: Optional[str] = None
        self.prev_hash: Optional[str] = bytearray(32).hex()
        self.devices: MutableMapping[str, Device] = {}

    def load(self) -> None:
        for entry in self.store.loader():
            self.prev_hash, entry_as_dict, self.error_reason = self.validate_entry(entry, self.prev_hash)
            if self.prev_hash is not None:
                self.raw_chain.append(entry)
                self.data_chain.append(entry_as_dict)
                stmt = entry_as_dict["statement"]
                stmt_keys = set(stmt.keys())
                if stmt_keys == ADD_DEVICE_KEYS:
                    self.devices[stmt["kid"]] = Device(stmt["device_id"], stmt["kid"], stmt["name"], stmt["kind"])
                elif stmt_keys == SIGNED_KID_KEYS:
                    self.devices[stmt["kid"]].signed_by_kid = entry_as_dict["authority"]["kid"]
            else:
                self.error_entry = entry
                self.error_entry_as_dict = entry_as_dict
                break

    def validate_entry(self, entry: str, prev_hash: Optional[str]) -> Tuple[Optional[str], dict, Optional[str]]:
        """validates an sigchain entry retrieved from a store

        sigchains are stored as base64 encoded strings - one entry per line

        For a valid entry, returns a tuple or the hash of the entry (to be checked against the next entry), the entry
        as a python dict and None for an error message
        For an invalid entry, return None for the hash, the entry as a dict, and an error message

        Note: the consumer may not easily type check against this type of structure
        """
        assert prev_hash is not None  # Deal with return None param # noqa: S101

        decoded_entry = base64.b64decode(entry)
        data = json.loads(decoded_entry[64:])
        if data["prev"] != prev_hash:
            return None, data, "Hash mismatch"
        try:
            vk = VerifyKey(data["authority"]["kid"], encoder=nacl.encoding.HexEncoder)
            vk.verify(decoded_entry)
        except BadSignatureError:
            return None, data, "Bad signature"

        return hashlib.sha256(bytes(entry, "utf-8")).hexdigest(), data, None

    def is_valid(self):
        return self.error_entry is None

    def __len__(self):
        return len(self.raw_chain)


def create_device_and_add_to_chain(chain: SigChain, name: str, account: str, kind: str) -> Optional[SigningKey]:
    did = random().hex()
    sk = SigningKey.generate()
    device = AddDevice(name, kind, did, sk)
    authority = Authority(account, sk)
    entry = Entry(device, authority, len(chain), chain.prev_hash)
    signed = base64.b64encode(entry.sign()).decode()

    if chain.is_valid():
        chain.store.adder(signed)
        chain.raw_chain.append(signed)
        chain.data_chain.append(entry.as_dict())
        chain.prev_hash = hashlib.sha256(bytes(signed, "utf-8")).hexdigest()
        kid = sk.verify_key.encode().hex()
        chain.devices[kid] = Device(did, kid, name, kind)
        return sk

    return None


def sign_kid_and_add_to_chain(chain: SigChain, kid: str, sk: SigningKey, account: str) -> None:
    statement = SignedKid(sk, kid)
    authority = Authority(account, sk)
    entry = Entry(statement, authority, len(chain), chain.prev_hash)
    signed = base64.b64encode(entry.sign()).decode()

    if chain.is_valid():
        chain.store.adder(signed)
        chain.raw_chain.append(signed)
        chain.data_chain.append(entry.as_dict())
        chain.prev_hash = hashlib.sha256(bytes(signed, "utf-8")).hexdigest()
        chain.devices[kid].signed_by_kid = sk.verify_key.encode().hex()


class Entry:
    def __init__(self, statement, authority, seq, prev=None):
        self.statement = statement
        self.authority = authority
        if prev is None:
            self.prev = bytearray(32).hex()
        else:
            self.prev = prev
        self.seq = seq
        self.sig = bytearray(64)

    def as_dict(self):
        return {
            "statement": self.statement.as_dict(),
            "authority": self.authority.as_dict(),
            "prev": self.prev,
            "seq": self.seq,
        }

    def sign(self):
        to_sign = json.dumps(self.as_dict())
        return self.authority.signing_key.sign(bytes(to_sign, "utf-8"))
