🗃 tdir - create and fill a temporary directory 🗃
======================================================

Run code inside a temporary directory filled with zero or more files.

Very convenient for writing tests: you can decorate individual tests or a whole
test suite.

``tdir()`` runs code in a temporary directory pre-filled with files: it can
either be used as a context manager, or a decorator for functions or classes.

``tdir.fill()`` is a tiny function that recursively fills a directory.

EXAMPLE: as a context manager

.. code-block:: python

    from pathlib import Path
    import tdir

    cwd = Path.cwd()

    # Simplest invocation.

    with tdir():
       # Do a lot of things in a temporary directory

    # Everything is gone!

    # With a single file
    with tdir('hello') as td:
        # The file ``hello`` is there
        assert Path('hello').read_text() = 'hello\n'

        # We're in a temporary directory
        assert td == Path.cwd()
        assert td != cwd

        # Write some other file
        Path('junk.txt').write_text('hello, world\n')

    # The temporary directory and the files are gone
    assert not td.exists()
    assert cwd == Path.cwd()

    # A more complex example:
    #
    with tdir(
        'one.txt',
        three='some information',
        four=Path('existing/file'),  # Copy a file into the tempdir
        sub1={
            'file.txt': 'blank lines\n\n\n\n',
            'sub2': [
                'a', 'b', 'c'
            ]
        },
    ):
        assert Path('one.txt').exists()
        assert Path('four').read_text() == Path('/existing/file').read_text()
        assert Path('sub1/sub2/a').exists()

    # All files gone!

EXAMPLE: as a decorator

.. code-block:: python

    from pathlib import Path
    import tdir
    import unittest

    @tdir
    def my_function():
        pass  # my_function() always operates in a temporary directory


    # Decorate a TestCase so each test runs in a new temporary directory
    # with two files
    @tdir('a', foo='bar')
    class MyTest(unittest.TestCast):
        def test_something(self):
            assert Path('a').read_text() = 'a\n'

        def test_something_else(self):
            assert Path('foo').read_text() = 'bar\n'


    class MyTest2(unittest.TestCast):
        # Decorate just one test in a unitttest
        @tdir(foo='bar', baz=bytes(range(4)))  # binary files are possible
        def test_something(self):
            assert Path('foo').read_text() = 'bar\n'
            assert Path('baz').read_bytes() = bytes(range(4)))

        # Run test in an empty temporary directory
        @tdir
        def test_something_else(self):
            assert not Path('a').exists()
            assert Path().absolute() != self.ORIGINAL_PATH

        ORIGINAL_PATH = Path().absolute()

API
---

Class ``tdir``
~~~~~~~~~~~~~~

(`tdir.py, 120-220 <https://github.com/rec/tdir/blob/master/tdir.py#L120-L220>`_)

Set up a temporary directory, fill it with files, then tear it down at
the end of an operation.

``tdir`` can be used either as a context manager, or a decorator for
functions or classes.

ARGUMENTS
  args, kwargs:
    Files to put into the temporary directory.
    See the documentation for ``tdir.fill()``

  chdir:
    If true (the default), change the working directory to the tdir at
    the start of the operation and restore the original working directory
    at the end.  Otherwise, don't change or restore the working directory.

  methods:
    The methods argument tells how to decorate class methods when
    decorating a class.

    The default decorates only class methods that start with the string
    ``test`` - exactly like ``unittest.mock.patch`` does.

    See https://github.com/rec/dek/blob/master/README.rst#dekdekdecorator-deferfalse-methodsnone

  use_dir:
    If non-empty, ``use_dir`` is used instead of a temp directory (and is
    not removed at the end) - for example, ``use_dir='.'`` puts everything in
    the current directory.

  save:
    If set to true, the temp directory is not deleted at end and its name
    is printed to ``sys.stderr``

``tdir.tdir.__new__()``
_______________________

.. code-block:: python

  tdir.tdir.__new__(
       cls,
       *args,
       chdir=True,
       methods='test',
       use_dir=None,
       save=False,
       **kwargs,
  )

(`tdir.py, 158-190 <https://github.com/rec/tdir/blob/master/tdir.py#L158-L190>`_)

Create and return a new object.  See help(type) for accurate signature.

``tdir.tdir.__call__(self, *args, **kwargs)``
_____________________________________________

(`tdir.py, 218-220 <https://github.com/rec/tdir/blob/master/tdir.py#L218-L220>`_)

Call self as a function.

``tdir.fill(root, *args, **kwargs)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(`tdir.py, 222-286 <https://github.com/rec/tdir/blob/master/tdir.py#L222-L286>`_)

Recursively fills a directory from file names and optional values.

ARGUMENTS
  root:
    The root directory to fill

  args:
    A list of strings, dictionaries or Paths.

    For strings, a file is created with that string as name and contents.

    For dictionaries, the contents are used to recursively create and fill
    the directory.

    For Paths, that file is copied into the target directory under the same
    name.

  kwargs:
    A dictionary mapping file or directory names to values.

    If the key's value is a string it is used to file a file of that name.

    If it's a dictionary, its contents are used to recursively create and
    fill a subdirectory.

    If it's a Path, that file is copied to the target directory but with
    the key as its name.

(automatically generated by `doks <https://github.com/rec/doks/>`_ on 2020-12-03T18:26:23.830491)
