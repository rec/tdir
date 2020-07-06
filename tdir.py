r"""
🗃 tdir - create and fill a temporary directory 🗃
======================================================

Creates a temporary directory using tempfile.TemporaryDirectory and then
populates it with files.  Great for tests!

* ``tdir`` is a context manager that runs in a populated temporary directory

* ``tdec`` is a decorator to run functions or test suites in a populated
  temporary directory

* ``fill`` recursively fills a directory (temporary or not)

EXAMPLE: to temporarily create a directory structure

.. code-block:: python

    import tdir

    with tdir.tdir(
        'one.txt', 'two.txt',
        three='some information',
        four=Path('/some/existing/file'),
        subdirectory1={
            'file.txt': 'blank lines\n\n\n\n',
            'subdirectory': ['a', 'b', 'c']
        },
    ):

EXAMPLE: as a decorator for tests

.. code-block:: python

    from pathlib import Path
    import tdir
    import unittest

    CWD = Path().absolute()


    # Decorate a whole class so each test runs in a new temporary directory
    @tdir('a', foo='bar')
    class MyTest(unittest.TestCast):
        def test_something(self):
            assert Path('a').read_text() = 'a\n'
            assert Path('foo').read_text() = 'bar\n'


    # Decorate single tests
    class MyTest(unittest.TestCast):
        @tdir(foo='bar', baz=bytes(range(4)))
        def test_something(self):
            assert Path('foo').read_text() = 'bar\n'
            assert Path('baz').read_bytes() = bytes(range(4)))

        # Run in an empty temporary directory
        @tdir
        def test_something_else(self):
            assert not Path('a').exists()
            assert Path().absolute() != CWD
"""
from dek import dek
from pathlib import Path
from unittest import mock
import contextlib
import os
import shutil
import tempfile

__all__ = 'tdir', 'tdec', 'fill'
__version__ = '0.11.1'


@contextlib.contextmanager
def tdir(*args, cwd=True, **kwargs):
    """
    A context manager to create and fill a temporary directory.

    ARGUMENTS
      args:
        A list of strings or dictionaries.  For strings, a file is created
        with that string as name and contents.  For dictionaries, the contents
        are used to recursively create and fill the directory.

      cwd:
        If true, change the working directory to the temp dir at the start
        of the context and restore the original working directory at the end.

      kwargs:
        A dictionary mapping file or directory names to values.
        If the key's value is a string it is used to file a file of that name.
        If it's a dictionary, its contents are used to recursively create and
        fill a subdirectory.
    """
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        fill(root, *args, **kwargs)
        if cwd:
            old_cwd = os.getcwd()
            os.chdir(td)
            try:
                yield root
            finally:
                os.chdir(old_cwd)
        else:
            yield root


@dek(methods=mock.patch.TEST_PREFIX)
def tdec(func, *args, cwd=True, **kwargs):
    """
    Decorate a function or ``unittest.TestCase`` so it runs in a populated
    temporary directory.

    If ``tdec()`` has exactly one callable argument, either a function or a
    class, ``tdec()`` decorates it to run in an empty temporary directory.

    Otherwise, ``tdec()`` returns a decorator which decorates a function or
    class to run a temporary directory populated with entries from args and
    kwargs/

    ARGUMENTS
      args:
        Either a single callable, or a list of strings or dictionaries.
        For strings, a file is created with that string as name and contents.
        For dictionaries, the contents are used to recursively create and
        fill the directory.

      cwd:
        If true, change the working directory to the temp dir at the start
        of the context and restore the original working directory at the end.

      kwargs:
        A dictionary mapping file or directory names to values.
        If the key's value is a string it is used to file a file of that name.
        If it's a dictionary, its contents are used to recursively create and
        fill a subdirectory.
    """
    with tdir(*args, cwd=cwd, **kwargs):
        func()


def fill(root, *args, **kwargs):
    """
    Recursively populate a directory.

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
