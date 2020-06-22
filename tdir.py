r"""
🗃 tdir - create and fill a temporary directory 🗃
======================================================

A context manager that creates a temporary directory using
tempfile.TemporaryDirectory and then populates it.

Extremely useful for unit tests where you want a whole directory
full of files really fast.

EXAMPLE

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

"""
from pathlib import Path
import contextlib
import os
import tempfile

__all__ = 'tdir', 'fill'
__version__ = '0.9.1'


@contextlib.contextmanager
def tdir(*args, cwd=True, **kwargs):
    """
    A context that creates and fills a temporary directory

    ARGUMENTS
      args:
        A list of string file names.  Each file is created and filled
        with the string value of its name.

      cwd:
        If true, change the working directory to the temp dir at the start
        of the context and restore the original working directory at the end.

      kwargs:
        A dictionary mapping file or directory names to values.
        If the key's value is a string it is used to file a file of that name.
        If it's a dictionary, its contents are used to recursively create and
        fill a directory.
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


def fill(root, *args, **kwargs):
    """
    Fill a directory with files containing strings

    ARGUMENTS
      root:
        The root directory to fill

      args:
        A list of string file names.  Each file is created and filled
        with the string value of its name.

      kwargs:
        A dictionary mapping file or directory names to values.
        If the key's value is a string it is used to file a file of that name.
        If it's a dictionary, its contents are used to recursively create and
        fill a directory.
    """
    if args:
        fill(root, **{a.strip(): a for a in args})

    for k, v in kwargs.items():
        rk = root / k
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
