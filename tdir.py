r"""
🗃 tdir - create and fill a temporary directory 🗃
======================================================

Create a temporary directory using tempfile.TemporaryDirectory and then
populate it.

* ``tdir`` is a context manager that runs in a populated temporary directory

* ``tdec`` is a decorator to run functions or test suites in a populated
  temporary directory

* ``fill`` recursively fills a directory (temporary or not)

Extremely useful for unit tests where you want a whole directory
full of files really fast.

EXAMPLE: to temporarily create a directory structure

.. code-block:: python

    import tdir

    with tdir.tdir(
        'one', 'two', 'three',
        four='two\nlines',
        sub1={
            'six': 'A short file',
            'seven': 'blank lines\n\n\n\n',
            'eight': ['a', 'b', 'c']
    }) as td:
        # Now the directory `td` has files `one`, `two` and `three`, each with
        # one line, file `four` with two lines, and then a subdirectory `sub/`
        # with more files.

EXAMPLE: as a decorator for tests

.. code-block:: python

    from pathlib import Path
    import tdir
    import unittest
    CWD = Path().absolute()


    # Decorate a whole class
    @tdir('a', 'b', foo='bar')
    class MyTest(unittest.TestCast):
        def test_something(self):
            assert Path('a').read_text() = 'a\n'
            assert Path('foo').read_text() = 'bar\n'


    # Decorate single tests
    class MyTest(unittest.TestCast):
        @tdir('a', 'b', foo='bar')
        def test_something(self):
            assert Path('a').read_text() = 'a\n'
            assert Path('foo').read_text() = 'bar\n'

        # Run in an empty temporary directory
        @tdir
        def test_something_else(self):
            assert not Path('a').exists()
            assert Path().absolute() != CWD
"""
from pathlib import Path
from unittest import mock
import contextlib
import functools
import os
import tempfile

__all__ = 'tdir', 'tdec', 'fill'
__version__ = '0.10.0'


@contextlib.contextmanager
def tdir(*args, cwd=True, **kwargs):
    """
    A context that creates and fills a temporary directory

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


def tdec(*args, **kwargs):
    """
    Decorate a function or TestCase so it runs in a temporary directory with
    file contents set.

    If args has exactly one element which is callable (either a function or a
    class), ``tdec`` returns that callable, but decorated.

    Otherwise, ``tdec`` returns a decorator to wrap functions so they get run
    in a temporary directory with data.
    """

    def wrap(args, kwargs, fn):
        def wrap_one(fn):
            @functools.wraps(fn)
            def wrapper(*args2, **kwargs2):
                with tdir(*args, **kwargs):
                    return fn(*args2, **kwargs2)

            return wrapper

        if not isinstance(fn, type):
            return wrap_one(fn)

        for attr in dir(fn):
            if attr.startswith(mock.patch.TEST_PREFIX):
                value = getattr(fn, attr)
                if callable(value):
                    setattr(fn, attr, wrap_one(value))
        return fn

    if len(args) == 1 and callable(args[0]):
        assert not kwargs
        return wrap((), {}, args[0])
    else:
        assert all(isinstance(i, (str, dict)) for i in args)
        assert all(isinstance(i, (str, dict)) for i in kwargs.values())

        return functools.partial(wrap, args, kwargs)


def fill(root, *args, **kwargs):
    """
    Fill a directory with files containing strings

    ARGUMENTS
      root:
        The root directory to fill

      args:
        A list of strings or dictionaries.  For strings, a file is created
        with that string as name and contents.  For dictionaries, the contents
        are used to recursively create and fill the directory.

      kwargs:
        A dictionary mapping file or directory names to values.
        If the key's value is a string it is used to file a file of that name.
        If it's a dictionary, its contents are used to recursively create and
        fill a subdirectory.
    """
    for a in args:
        if isinstance(a, str):
            a = {a.strip(): a}
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

        elif isinstance(v, (bytes, bytearray)):
            rk.write_bytes(v)

        elif isinstance(v, dict):
            fill(rk, **v)

        elif isinstance(v, (list, tuple)):
            fill(rk, *v)

        else:
            raise TypeError('Do not understand type %s of %s' % (v, type(v)))
