r"""
# 🗃 tdir - create and fill a temporary directory 🗃

Run code inside a temporary directory filled with zero or more files.

Very convenient for writing tests: you can decorate individual tests or a whole
test suite.

`tdir()` runs code in a temporary directory pre-filled with files: it can
either be used as a context manager, or a decorator for functions or classes.

`tdir.fill()` is a tiny function that recursively fills a directory.

## Example: as a context manager

    from pathlib import Path
    import tdir

    cwd = Path.cwd()

    # Simplest invocation.

    with tdir():
       # Do a lot of things in a temporary directory

    # Everything is gone!

    # With a single file
    with tdir('hello') as td:
        # The file `hello` is there
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

## Example: as a decorator

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
"""
from __future__ import annotations

import dataclasses as dc
import os
import shutil
import sys
import tempfile
import threading
import traceback
import typing as t
from pathlib import Path
from types import TracebackType
from unittest.mock import patch

import dek
import xmod

__all__ = 'tdir', 'fill'

Arg = t.Union[str, Path, t.Dict[str, t.Any]]


@xmod.xmod
def tdir(
    *args: Arg,
    chdir: bool = True,
    clear: bool = False,
    methods: str = patch.TEST_PREFIX,
    save: bool = False,
    use_dir: str = '',
    **kwargs: Arg,
) -> '_Tdir':
    """
    Set up a temporary directory, fill it with files, then tear it down at
    the end of an operation.

    `tdir` can be used either as a context manager, or a decorator for
    functions or classes.

    ARGUMENTS
      args, kwargs:
        Files to put into the temporary directory.
        See the documentation for `tdir.fill()`

      chdir:
        If true (the default), change the working directory to the tdir at
        the start of the operation and restore the original working directory
        at the end.  Otherwise, don't change or restore the working directory.

      methods:
        The methods argument tells how to decorate class methods when
        decorating a class.

        The default decorates only class methods that start with the string
        `test` - exactly like `unittest.mock.patch` does.

      use_dir:
        If non-empty, `use_dir` is used instead of a temp directory (and is
        not removed at the end) - for example, `use_dir='.'` puts everything in
        the current directory.

      save:
        If set to true, the temp directory is not deleted at end and its name
        is printed to `sys.stderr`
    """
    td: _Tdir

    @dek.dek(methods=methods)
    def call(func, *args, **kwargs) -> None:
        with td:
            func(*args, **kwargs)

    is_decorator = len(args) == 1 and callable(args[0]) and not kwargs
    if is_decorator:
        decorator = args[0]
        args = ()

    d = dict(locals())
    fields = (f.name for f in dc.fields(_Tdir))
    td = _Tdir(**{f: d[f] for f in fields})
    return td(decorator) if is_decorator else td


@dc.dataclass
class _Tdir:
    args: t.Sequence[Arg]
    call: t.Callable
    chdir: bool
    clear: bool
    kwargs: t.Dict[str, Arg]
    save: bool
    use_dir: str

    def __enter__(self) -> Path:
        if self.use_dir:
            self.directory = Path(self.use_dir)
        else:
            suffix = f'-{threading.get_ident()}-{os.getpid()}'
            self._td = tempfile.TemporaryDirectory(suffix=suffix)
            self.directory = Path(self._td.__enter__())

        if self.clear:
            for f in self.directory.iterdir():
                if f.is_dir():
                    shutil.rmtree(f)
                else:
                    f.unlink()

        fill(self.directory, *self.args, **self.kwargs)

        if self.chdir:
            self.old_directory = os.getcwd()
            os.chdir(self.directory)

        return self.directory

    def __exit__(
        self,
        exc_type: t.Optional[t.Type[BaseException]],
        exc_val: t.Optional[BaseException],
        exc_tb: t.Optional[TracebackType],
    ) -> None:
        if self.chdir:
            try:
                os.chdir(self.old_directory)
            except Exception:  # pragma: no cover
                traceback.print_exc()

        if self.save:
            msg = f'🗃 tdir saving {self.directory.absolute()} 🗃'
            print(msg, file=sys.stderr)

        elif not self.use_dir:
            self._td.__exit__(exc_type, exc_val, exc_tb)

    def __call__(self, *args, **kwargs) -> t.Any:
        return self.call(*args, **kwargs)


def fill(_root: t.Union[str, Path], *args: Arg, **kwargs: Arg) -> None:
    """
    Recursively fills a directory from file names and optional values.

    ARGUMENTS
      _root:
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
    """
    _root = Path(_root)
    for a in args:
        if isinstance(a, str):
            a = {a.strip(): a}
        elif isinstance(a, Path):
            a = {a.name: a}
        elif not isinstance(a, dict):
            raise TypeError('Do not understand type %s of %s' % (a, type(a)))
        fill(_root, **a)

    for k, v in kwargs.items():
        rk = _root / k
        is_dir = isinstance(v, (dict, list, tuple))
        to_make = rk if is_dir else rk.parent
        to_make.mkdir(parents=True, exist_ok=True)

        if isinstance(v, str):
            if not v.endswith('\n'):
                v += '\n'
            rk.write_text(v)

        elif isinstance(v, Path):
            if v.is_dir():
                shutil.copytree(str(v), str(rk))
            else:
                shutil.copyfile(str(v), str(rk))

        elif isinstance(v, (bytes, bytearray)):
            rk.write_bytes(v)

        elif isinstance(v, dict):
            fill(rk, **v)

        elif isinstance(v, (list, tuple)):
            fill(rk, *v)

        else:
            raise TypeError('Do not understand type %s=%s' % (k, v))
