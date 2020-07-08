from pathlib import Path
from tdir import fill, tdir
import sys
import unittest

CWD = Path().absolute()


class TestTdir(unittest.TestCase):
    def test_simple_cwd(self):
        with tdir('a', 'b', 'c') as td:
            assert sorted(i.name for i in td.iterdir()) == ['a', 'b', 'c']
            for i in 'abc':
                assert Path(i).read_text() == i + '\n'

    def test_simple(self):
        with tdir('a', 'b', {'c': 'c'}, cwd=False) as td:
            assert sorted(i.name for i in td.iterdir()) == ['a', 'b', 'c']
            for i in 'abc':
                assert (td / i).read_text() == i + '\n'
                assert not Path(i).exists()

    def test_dict(self):
        with tdir(one='ONE', two='TWO') as td:
            assert sorted(i.name for i in td.iterdir()) == ['one', 'two']
            for i in ('one', 'two'):
                assert (td / i).read_text() == i.upper() + '\n'

    def test_binary(self):
        with tdir(one=b'ONE', two=bytearray(b'TWO')) as td:
            assert sorted(i.name for i in td.iterdir()) == ['one', 'two']
            for i in ('one', 'two'):
                assert (td / i).read_bytes() == i.upper().encode()

    def test_list(self):
        with tdir(sub=['one', 'two']) as td:
            sub = td / 'sub'
            assert sorted(i.name for i in sub.iterdir()) == ['one', 'two']
            for i in ('one', 'two'):
                assert (sub / i).read_text() == i + '\n'

    def test_path1(self):
        path = Path(__file__)
        with tdir(path):
            expected = path.read_text()
            actual = Path(path.name).read_text()
            assert expected == actual

    def test_path2(self):
        path = Path(__file__)
        with tdir(foo=path):
            expected = path.read_text()
            actual = Path('foo').read_text()
            assert expected == actual

    def test_eror(self):
        with tdir():
            with self.assertRaises(TypeError) as m:
                fill('.', foo=3)
        assert m.exception.args[0].startswith('Do not understand type')

        with self.assertRaises(TypeError) as m:
            with tdir(None):
                pass
        assert m.exception.args[0].startswith('Do not understand type')

    def test_big(self):
        items = {
            'foo': {
                '__init__.py': 'TEST = 32\n',
                'toast.py': 'from . import TEST as TOAST\n',
            },
            'bar': {
                '__init__.py': 'import foo\nTEST = foo.TEST - 9\n',
                'toast.py': 'from . import TEST as TOAST\n',
            },
            'bang.py': 'TEST = 5\n',
            'data': ['a', 'b', 'c'],
        }

        with tdir(**items) as td:
            sys_path = sys.path[:]
            sys.path.insert(0, str(td))

            try:
                import bang
                import foo.toast
                import bar.toast

            finally:
                sys.path[:] = sys_path

            assert bang.TEST == 5
            assert foo.toast.TOAST == 32
            assert bar.toast.TOAST == 23
            for i in 'abc':
                assert (td / 'data' / i).read_text() == i + '\n'

        with tdir(items) as td:
            sys_path = sys.path[:]
            sys.path.insert(0, str(td))

            try:
                import bang
                import foo.toast
                import bar.toast

            finally:
                sys.path[:] = sys_path

            assert bang.TEST == 5
            assert foo.toast.TOAST == 32
            assert bar.toast.TOAST == 23
            for i in 'abc':
                assert (td / 'data' / i).read_text() == i + '\n'


@tdir
class TestTdirClass1(unittest.TestCase):
    def test_not_in_root(self):
        cwd = str(Path().absolute())
        assert cwd != CWD


@tdir()
class TestTdirClass2(unittest.TestCase):
    def test_not_in_root(self):
        cwd = str(Path().absolute())
        assert cwd != CWD


@tdir('a', foo='bar')
class TestTdirClass3(unittest.TestCase):
    test_variable = 3

    def test_values(self):
        assert Path('a').read_text() == 'a\n'
        assert Path('foo').read_text() == 'bar\n'


class TestTdirClass4(unittest.TestCase):
    @tdir
    def test_not_in_root(self):
        cwd = str(Path().absolute())
        assert cwd != CWD

    @tdir()
    def test_not_in_root2(self):
        cwd = str(Path().absolute())
        assert cwd != CWD

    @tdir('a', foo='bar')
    def test_values(self):
        assert Path('a').read_text() == 'a\n'
        assert Path('foo').read_text() == 'bar\n'
