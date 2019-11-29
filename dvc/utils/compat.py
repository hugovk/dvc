"""Handle import compatibility between Python 2 and Python 3"""

import errno
import os
import sys
from contextlib import contextmanager

# simplified version of ipython_genutils/encoding.py
DEFAULT_ENCODING = sys.getdefaultencoding()


def encode(u, encoding=None):
    encoding = encoding or DEFAULT_ENCODING
    return u.encode(encoding, "replace")


def csv_reader(unicode_csv_data, dialect=None, **kwargs):
    """csv.reader doesn't support Unicode input, so need to use some tricks
    to work around this.

    Source: https://docs.python.org/2/library/csv.html#csv-examples
    """
    import csv

    dialect = dialect or csv.excel

    # Python3 supports encoding by default, so just return the object
    for row in csv.reader(unicode_csv_data, dialect=dialect, **kwargs):
        yield [cell for cell in row]


def utf_8_encoder(unicode_csv_data):
    """Source: https://docs.python.org/2/library/csv.html#csv-examples"""
    for line in unicode_csv_data:
        yield line.encode("utf-8")


def cast_bytes(s, encoding=None):
    """Source: https://github.com/ipython/ipython_genutils"""
    if not isinstance(s, bytes):
        return encode(s, encoding)
    return s


def _makedirs(name, mode=0o777, exist_ok=False):
    """Source: https://github.com/python/cpython/blob/
        3ce3dea60646d8a5a1c952469a2eb65f937875b3/Lib/os.py#L196-L226
    """
    head, tail = os.path.split(name)
    if not tail:
        head, tail = os.path.split(head)
    if head and tail and not os.path.exists(head):
        try:
            _makedirs(head, exist_ok=exist_ok)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        cdir = os.curdir
        if tail == cdir:
            return
    try:
        os.mkdir(name, mode)
    except OSError:
        if not exist_ok or not os.path.isdir(name):
            raise


@contextmanager
def ignore_file_not_found():
    try:
        yield
    except OSError as exc:
        if exc.errno != errno.ENOENT:
            raise


# Backport os.fspath() from Python 3.6
try:
    from os import fspath  # noqa: F821

    fspath_py35 = lambda s: s  # noqa: E731
except ImportError:

    def fspath(path):
        """Return the path representation of a path-like object.

        If str or bytes is passed in, it is returned unchanged. Otherwise the
        os.PathLike interface is used to get the path representation. If the
        path representation is not str or bytes, TypeError is raised. If the
        provided path is not str, bytes, or os.PathLike, TypeError is raised.
        """
        if isinstance(path, (str, bytes)):
            return path

        # Work from the object's type to match method resolution of other magic
        # methods.
        path_type = type(path)
        try:
            path_repr = path_type.__fspath__(path)
        except AttributeError:
            if hasattr(path_type, "__fspath__"):
                raise
            else:
                raise TypeError(
                    "expected str, bytes or os.PathLike object, "
                    "not " + path_type.__name__
                )
        if isinstance(path_repr, (str, bytes)):
            return path_repr
        else:
            raise TypeError(
                "expected {}.__fspath__() to return str or bytes, "
                "not {}".format(path_type.__name__, type(path_repr).__name__)
            )

    fspath_py35 = fspath
