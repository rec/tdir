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

API
---

Class `tdir.tdir``
~~~~~~~~~~~~~~~~~~

(`tdir.py, 81-149 <https://github.com/rec/tdir/blob/master/tdir.py#L81-L149>`_)

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
    https://github.com/rec/dek/blob/master/README.rst#dekdekdecorator-deferfalse-methodsnone

``tdir.tdir.__new__(cls, *args, cwd=True, methods='test', **kwargs)``
_____________________________________________________________________

(`tdir.py, 105-127 <https://github.com/rec/tdir/blob/master/tdir.py#L105-L127>`_)

Create and return a new object.  See help(type) for accurate signature.

``tdir.tdir.__enter__(self)``
_____________________________

(`tdir.py, 128-139 <https://github.com/rec/tdir/blob/master/tdir.py#L128-L139>`_)


``tdir.tdir.__exit__(self, *args)``
___________________________________

(`tdir.py, 140-146 <https://github.com/rec/tdir/blob/master/tdir.py#L140-L146>`_)


``tdir.tdir.__call__(self, *args, **kwargs)``
_____________________________________________

(`tdir.py, 147-149 <https://github.com/rec/tdir/blob/master/tdir.py#L147-L149>`_)

Call self as a function.

Class `tdir.tdec``
~~~~~~~~~~~~~~~~~~

(`tdir.py, 81-149 <https://github.com/rec/tdir/blob/master/tdir.py#L81-L149>`_)

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
    https://github.com/rec/dek/blob/master/README.rst#dekdekdecorator-deferfalse-methodsnone

``tdir.tdec.__new__(cls, *args, cwd=True, methods='test', **kwargs)``
_____________________________________________________________________

(`tdir.py, 105-127 <https://github.com/rec/tdir/blob/master/tdir.py#L105-L127>`_)

Create and return a new object.  See help(type) for accurate signature.

``tdir.tdec.__enter__(self)``
_____________________________

(`tdir.py, 128-139 <https://github.com/rec/tdir/blob/master/tdir.py#L128-L139>`_)


``tdir.tdec.__exit__(self, *args)``
___________________________________

(`tdir.py, 140-146 <https://github.com/rec/tdir/blob/master/tdir.py#L140-L146>`_)


``tdir.tdec.__call__(self, *args, **kwargs)``
_____________________________________________

(`tdir.py, 147-149 <https://github.com/rec/tdir/blob/master/tdir.py#L147-L149>`_)

Call self as a function.

``tdir.fill(root, *args, **kwargs)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(`tdir.py, 154-216 <https://github.com/rec/tdir/blob/master/tdir.py#L154-L216>`_)

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

(automatically generated by `doks <https://github.com/rec/doks/>`_ on 2020-07-10T16:03:56.532666)
