# source:
# https://stackoverflow.com/questions/26949134/python-3-4-extending-pathlib-path

import os
import pathlib
from shutil import rmtree


class Path(pathlib.Path):

    def __new__(cls, *args, **kwargs):
        if cls is Path:
            cls = WindowsPath if os.name == 'nt' else PosixPath
        self = cls._from_parts(args, init=False)
        if not self._flavour.is_supported:
            raise NotImplementedError("cannot instantiate %r on your system"
                                      % (cls.__name__,))
        self._init()
        return self

    def ls(self, pat='*'):
        ''' List the folder '''
        if self.exists():
            return [f.name for f in self.glob(pat)]
        return []

    def rmtree(self, ignore_errors=False, onerror=None):
        """
        Delete the entire directory even if it contains directories / files.
        """
        rmtree(str(self), ignore_errors, onerror)

    def go(self):
        ''' Go to this folder '''
        os.chdir(str(self.absolute()))


class PosixPath(Path, pathlib.PurePosixPath):
    __slots__ = ()


class WindowsPath(Path, pathlib.PureWindowsPath):
    __slots__ = ()
