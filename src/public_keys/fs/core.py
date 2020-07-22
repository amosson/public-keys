import errno
import io
import os
from typing import Dict

from fuse import FuseOSError, Operations  # type: ignore
from saltpack.encrypt import decrypt, encrypt  # type: ignore


class Passthrough(Operations):
    def __init__(self, root):
        self.root = root

    # Helpers
    # =======

    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.root, partial)
        return path

    # Filesystem methods
    # ==================

    def access(self, path, mode):
        full_path = self._full_path(path)
        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        full_path = self._full_path(path)
        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        full_path = self._full_path(path)  # pragma: nocover
        return os.chown(full_path, uid, gid)  # pragma: nocover  # don't want to fiddle with Sudo for tests:w

    def getattr(self, path, fh=None):
        full_path = self._full_path(path)
        st = os.lstat(full_path)
        return dict(
            (key, getattr(st, key))
            for key in ("st_atime", "st_ctime", "st_gid", "st_mode", "st_mtime", "st_nlink", "st_size", "st_uid")
        )

    def readdir(self, path, fh):
        full_path = self._full_path(path)

        dirents = [".", ".."]
        if os.path.isdir(full_path):  # pragma: nocover
            dirents.extend(os.listdir(full_path))
        for r in dirents:
            yield r

    def readlink(self, path):
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.root)
        else:  # pragma: nocover
            return pathname

    def mknod(self, path, mode, dev):
        return os.mknod(self._full_path(path), mode, dev)  # pragma: nocover

    def rmdir(self, path):
        full_path = self._full_path(path)
        return os.rmdir(full_path)

    def mkdir(self, path, mode):
        return os.mkdir(self._full_path(path), mode)

    def statfs(self, path):
        full_path = self._full_path(path)
        stv = os.statvfs(full_path)
        return dict(
            (key, getattr(stv, key))
            for key in (
                "f_bavail",
                "f_bfree",
                "f_blocks",
                "f_bsize",
                "f_favail",
                "f_ffree",
                "f_files",
                "f_flag",
                "f_frsize",
                "f_namemax",
            )
        )

    def unlink(self, path):
        return os.unlink(self._full_path(path))

    def symlink(self, name, target):
        return os.symlink(target, self._full_path(name))

    def rename(self, old, new):
        return os.rename(self._full_path(old), self._full_path(new))  # pragma: nocover

    def link(self, target, name):
        return os.link(self._full_path(name), self._full_path(target))  # pragma: nocover

    def utimens(self, path, times=None):
        return os.utime(self._full_path(path), times)  # pragma: nocover

    # File methods
    # ============

    def open(self, path, flags):
        full_path = self._full_path(path)
        return os.open(full_path, flags)

    def flush(self, path, fh):
        return os.fsync(fh)

    def release(self, path, fh):
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        return self.flush(path, fh)


class EncryptedFS(Passthrough):
    def __init__(self, root: str, pub: bytes, priv: bytes) -> None:
        super().__init__(root)
        self.pub = pub
        self.priv = priv
        self.open_files: Dict[int, io.BytesIO] = {}
        self.dirty_files: Dict[int, bool] = {}
        self.total_bytes: int = 0

    def decrypt(self, fh: int) -> io.BytesIO:
        try:
            f = self.open_files[fh]
        except KeyError:
            f = io.BytesIO()
            self.open_files[fh] = f

        # if len(f.getvalue()) == 0:
        encrypted = io.BytesIO()
        chunk = os.read(fh, 2048)
        encrypted.write(chunk)
        while chunk != b"":
            chunk = os.read(fh, 2048)
            encrypted.write(chunk)

        if len(encrypted.getvalue()) > 0:
            f.write(decrypt(encrypted.getvalue(), self.priv))

        return f

    def create(self, path, mode, fi=None):
        print("create - " + path)
        full_path = self._full_path(path)
        fd = os.open(full_path, os.O_RDWR | os.O_CREAT, mode)
        self.open_files[fd] = io.BytesIO()
        self.dirty_files[fd] = False
        return fd

    def open(self, path, flags) -> int:
        print("open - " + path)
        fd = super().open(path, os.O_RDWR)
        self.open_files[fd] = self.decrypt(fd)
        self.dirty_files[fd] = False
        return fd

    def read(self, path, length, offset, fh) -> bytes:
        print("read - ")
        f = self.open_files[fh]
        f.seek(offset)
        return f.read(length)

    def write(self, path, buf, offset, fh) -> int:
        print("write - ")
        f = self.open_files[fh]
        self.dirty_files[fh] = True
        f.seek(offset)
        return f.write(buf)

    def encrypt(self, fh: int) -> bytes:
        return encrypt(self.priv, [self.pub], self.open_files[fh].getvalue(), 10 ** 6)

    def flush(self, path, fh):
        print("flush - ")
        if self.dirty_files[fh]:
            os.ftruncate(fh, 0)
            os.lseek(fh, 0, os.SEEK_SET)
            os.write(fh, self.encrypt(fh))
            self.dirty_files[fh] = False
        return super().flush(path, fh)

    def release(self, path, fh):
        print("release - ")
        del self.open_files[fh]
        del self.dirty_files[fh]
        return super().release(path, fh)

    def truncate(self, path, length, fh=None):
        fh = self.open(path, os.O_RDWR)
        self.open_files[fh] = io.BytesIO(self.open_files[fh].getvalue()[:length])
        self.dirty_files[fh] = True
        self.flush(path, fh)
        self.release(path, fh)
