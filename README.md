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


### [API Documentation](https://rec.github.io/tdir#tdir--api-documentation)
