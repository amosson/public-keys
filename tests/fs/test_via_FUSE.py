import os
import signal
from multiprocessing import Process
from tempfile import TemporaryDirectory
from time import sleep

import pytest
from fuse import FUSE  # type: ignore  # noqa: I100
from nacl.public import PrivateKey  # type: ignore
from saltpack.encrypt import decrypt, encrypt  # type: ignore

from public_keys.fs.core import EncryptedFS


@pytest.fixture(scope="session")
def fuse_fs():
    def run_fuse(fs, mp):
        FUSE(fs, mp, nothreads=True, foreground=True)

    print("fixture")
    pk = PrivateKey.generate()
    with TemporaryDirectory() as root:
        with TemporaryDirectory() as mp:
            efs = EncryptedFS(root, pk.public_key.encode(), pk.encode())

            p = Process(target=run_fuse, args=(efs, mp))
            p.start()
            sleep(1)
            print(p.pid)
            yield root, mp, pk
            os.kill(p.pid, signal.SIGINT)
            p.join()


def test_read_write(fuse_fs) -> None:
    print("test method")
    fn = fuse_fs[1] + "/test_read_write"
    with open(fn, "w") as f:
        f.write("this is a test message")

    with open(fn, "r") as f:
        assert "this is a test message" == f.read()


def test_write(fuse_fs) -> None:
    print("test method")
    fn = fuse_fs[1] + "/test_write"
    fnr = fuse_fs[0] + "/test_write"
    with open(fn, "w") as f:
        f.write("this is a test message")

    with open(fnr, "rb") as fb:
        assert b"this is a test message" == decrypt(fb.read(), fuse_fs[2].encode())


def test_read(fuse_fs) -> None:
    fnr = fuse_fs[1] + "/test_read"
    fnw = fuse_fs[0] + "/test_read"
    with open(fnw, "wb") as f:
        f.write(encrypt(fuse_fs[2].encode(), [fuse_fs[2].public_key.encode()], b"this is a test message", 10 ** 6))

    with open(fnr, "r") as ft:
        assert "this is a test message" == ft.read()


def test_chmod_and_access(fuse_fs) -> None:
    fnf = fuse_fs[1] + "/test_chmod_and_access"

    with open(fnf, "w") as f:
        f.write("this is a test message")

    os.chmod(fnf, 0o0000)
    with pytest.raises(PermissionError):
        f = open(fnf, "r")

    assert not os.access(fnf, os.R_OK)


def test_scandir(fuse_fs) -> None:
    assert len(list(os.scandir(fuse_fs[1]))) > 1


def test_scandir_subdir(fuse_fs) -> None:
    os.mkdir(fuse_fs[1] + "/test_scandir_with_subdir")
    with open(fuse_fs[1] + "/test_scandir_with_subdir/afile", "w") as f:
        f.write("this is a test message")
    assert len(list(os.scandir(fuse_fs[1]))) > 3


def test_readlink(fuse_fs) -> None:
    os.symlink(fuse_fs[1] + "/test_read", fuse_fs[1] + "/test_read-link")
    with open(fuse_fs[1] + "/test_read-link", "r") as f:
        assert "this is a test message" == f.read()


def test_rmdir(fuse_fs) -> None:
    os.mkdir(fuse_fs[1] + "/test_rmdir")
    os.rmdir(fuse_fs[1] + "/test_rmdir")
    with pytest.raises(FileNotFoundError):
        os.stat(fuse_fs[1] + "/test_rmdir")


def test_statfs(fuse_fs) -> None:
    assert os.statvfs(fuse_fs[1])


def test_unlink(fuse_fs) -> None:
    os.symlink(fuse_fs[1] + "/test_read", fuse_fs[1] + "/test_read-unlink")
    os.unlink(fuse_fs[1] + "/test_read-unlink")
