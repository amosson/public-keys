import os
from tempfile import TemporaryDirectory

from nacl.public import PrivateKey  # type: ignore
from saltpack.encrypt import decrypt, encrypt  # type: ignore

from public_keys.fs.core import EncryptedFS


def test_basic_write_read() -> None:
    pk = PrivateKey.generate()
    with TemporaryDirectory() as d:
        efs = EncryptedFS(d, pk.public_key.encode(), pk.encode())

        fd = efs.create("f1", 0o777)
        efs.write("", b"this is a message", 0, fd)
        efs.flush("", fd)
        efs.release("", fd)

        fdr = efs.open("f1", os.O_RDONLY)
        assert b"this is a message" == efs.read("f1", 2048, 0, fdr)


def test_basic_write() -> None:
    pk = PrivateKey.generate()
    with TemporaryDirectory() as d:
        efs = EncryptedFS(d, pk.public_key.encode(), pk.encode())

        fd = efs.create("f1", 0o777)
        efs.write("", b"this is a message", 0, fd)
        efs.fsync("", 0, fd)
        efs.flush("", fd)
        efs.release("", fd)

        with open(d + "/f1", "rb") as f:
            assert b"this is a message" == decrypt(f.read(), pk.encode())


def test_basic_read() -> None:
    pk = PrivateKey.generate()
    with TemporaryDirectory() as d:
        efs = EncryptedFS(d, pk.public_key.encode(), pk.encode())

        with open(d + "/f1", "wb") as f:
            f.write(encrypt(pk.encode(), [pk.public_key.encode()], b"this is a message", 10 ** 6))

        fd = efs.open("f1", os.O_RDONLY)
        assert b"this is a message" == efs.read("", 2048, 0, fd)


def test_flush_clean_does_not_update_mtime() -> None:
    pk = PrivateKey.generate()
    with TemporaryDirectory() as d:
        efs = EncryptedFS(d, pk.public_key.encode(), pk.encode())

        fd = efs.create("f1", 0o777)
        efs.write("", b"this is a message", 0, fd)
        efs.flush("", fd)
        mtime = os.fstat(fd).st_mtime
        efs.flush("", fd)
        efs.release("", fd)
        assert mtime == os.stat(d + "/f1").st_mtime


def test_read_empty_file() -> None:
    pk = PrivateKey.generate()
    with TemporaryDirectory() as d:
        efs = EncryptedFS(d, pk.public_key.encode(), pk.encode())

        fd = efs.create("f1", 0o777)
        efs.flush("", fd)
        efs.release("", fd)

        fdr = efs.open("f1", os.O_RDONLY)
        assert b"" == efs.read("f1", 2048, 0, fdr)


def test_truncate() -> None:
    pk = PrivateKey.generate()
    with TemporaryDirectory() as d:
        efs = EncryptedFS(d, pk.public_key.encode(), pk.encode())

        fd = efs.create("f1", 0o777)
        efs.write("", b"this is a message", 0, fd)
        efs.flush("", fd)
        efs.release("", fd)

        efs.truncate("f1", 6)
        fdr = efs.open("f1", os.O_RDONLY)
        assert b"this is a message"[:6] == efs.read("", 2048, 0, fdr)
        efs.release("f1", fdr)
