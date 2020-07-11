r"""
🗃 tdir - create and fill a temporary directory 🗃
======================================================

Creates a temporary directory using tempfile.TemporaryDirectory and then
fills it with files.  Great for tests!

``tdir`` is a context manager and decorator that runs functions or test
suites in a temporary directory filled with files

``fill`` recursively fills a directory (temporary or not)

EXAMPLE: as a context manager

.. code-block:: python

    import tdir

    with tdir(
        'one.txt', 'two.txt',
        three='some information',
        four=Path('/some/existing/file'),
        subdirectory1={
            'file.txt': 'blank lines\n\n\n\n',
            'subdirectory': ['a', 'b', 'c']
        },
    ):

EXAMPLE: as a decorator

.. code-block:: python

    from pathlib import Path
    import unittest

    @tdir
    def my_function():
        # Do some work in a temporary directory


    # Decorate a TestCase so each test runs in a new temporary directory
    @tdir('a', foo='bar')
    class MyTest(unittest.TestCast):
        def test_something(self):
            assert Path('a').read_text() = 'a\n'

        def test_something_else(self):
            assert Path('foo').read_text() = 'bar\n'


    # Decorate single test in a unitttest
    class MyTest2(unittest.TestCast):
        @tdir(foo='bar', baz=bytes(range(4)))  # binary files are possible
        def test_something(self):
            assert Path('foo').read_text() = 'bar\n'
            assert Path('baz').read_bytes() = bytes(range(4)))

        # Run in an empty temporary directory
        @tdir
        def test_something_else(self):
            assert not Path('a').exists()
            assert Path().absolute() != self.ORIGINAL_PATH

        ORIGINAL_PATH = Path().absolute()

"""
from pathlib import Path
from unittest.mock import patch
import clod
import dek
import os
import shutil
import tempfile
import traceback

__all__ = 'tdir', 'tdec', 'fill'
__version__ = '0.12.0'


class tdir:
    """
    Set up a temporary directory, fill it with files, then tear it down at
    the end of an operation.

    ``tdir`` can be used either as a context manager, or a decorator that
    works on functions or classes.

    ARGUMENTS
      args, kwargs:
        Files to put into the temporary directory.
        See the documentation for ``tdir.fill()``

      cwd:
        If True (the default), change the working directory to the tdir at
        the start of the operation and restore the original working directory
        at the end.

      methods:
        Which methods on classes to decorate.  See
        https://github.com/rec/dek/blob/master/README.rst\
#dekdekdecorator-deferfalse-methodsnone
    """

    def __new__(cls, *args, cwd=True, methods=patch.TEST_PREFIX, **kwargs):
        is_decorator = len(args) == 1 and callable(args[0]) and not kwargs
        if is_decorator:
            decorator = args[0]
            args = ()

        obj = super(tdir, cls).__new__(cls)
        obj.args = args
        obj.kwargs = dict(kwargs)
        obj.cwd = cwd

        @dek(methods=methods)
        def call(func, *args, **kwargs):
            with obj:
                func(*args, **kwargs)

        obj._call = call

        if is_decorator:
            return obj(decorator)

        return obj

    def __enter__(self):
        self.td = tempfile.TemporaryDirectory()
        td = self.td.__enter__()

        root = Path(td)
        fill(root, *self.args, **self.kwargs)
        if self.cwd:
            self.old_cwd = os.getcwd()
            os.chdir(td)

        return root

    def __exit__(self, *args):
        try:
            os.chdir(self.old_cwd)
        except Exception:
            traceback.print_exc()
        return self.td.__exit__(*args)

    def __call__(self, *args, **kwargs):
        return self._call(*args, **kwargs)


tdec = tdir  # DEPRECATED


def fill(root, *args, **kwargs):
    """
    Recursively fills a directory.

    ARGUMENTS
      root:
        The root directory to fill

      args:
        A list of strings, dictionaries or Paths.

        For strings, a file is created with that string as name and contents.

        For dictionaries, the contents are used to recursively create and fill
        the directory.

        For Paths, the file is copied into the target directory

      kwargs:
        A dictionary mapping file or directory names to values.

        If the key's value is a string it is used to file a file of that name.

        If it's a dictionary, its contents are used to recursively create and
        fill a subdirectory.

        If it's a Path, that file is copied to the target directory.
    """
    for a in args:
        if isinstance(a, str):
            a = {a.strip(): a}
        elif isinstance(a, Path):
            a = {a.name: a}
        elif not isinstance(a, dict):
            raise TypeError('Do not understand type %s of %s' % (a, type(a)))
        fill(root, **a)

    for k, v in kwargs.items():
        rk = Path(root) / k
        is_dir = isinstance(v, (dict, list, tuple))
        to_make = rk if is_dir else rk.parent
        to_make.mkdir(parents=True, exist_ok=True)

        if isinstance(v, str):
            if not v.endswith('\n'):
                v += '\n'
            rk.write_text(v)

        elif isinstance(v, Path):
            shutil.copyfile(str(v), str(rk))

        elif isinstance(v, (bytes, bytearray)):
            rk.write_bytes(v)

        elif isinstance(v, dict):
            fill(rk, **v)

        elif isinstance(v, (list, tuple)):
            fill(rk, *v)

        else:
            raise TypeError('Do not understand type %s of %s' % (v, type(v)))


clod(tdir, __name__)
