from pathlib import Path
import os
import shutil
import sys
import tdir
import unittest

CWD = Path().absolute()


class TestTdir(unittest.TestCase):
    def test_simple_cwd(self):
        with tdir('a', 'b', 'c') as td:
            assert sorted(i.name for i in td.iterdir()) == ['a', 'b', 'c']
            for i in 'abc':
                assert Path(i).read_text() == i + '\n'

    def test_simple(self):
        with tdir('a', 'b', {'c': 'c'}, chdir=False) as td:
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

    def test_error(self):
        with tdir():
            with self.assertRaises(TypeError) as m:
                tdir.fill('.', foo=3)
        assert m.exception.args[0].startswith('Do not understand type')

        with self.assertRaises(TypeError) as m:
            with tdir(None):
                pass
        assert m.exception.args[0].startswith('Do not understand type')

    @tdir
    def test_usedir(self):
        cwd = os.getcwd()
        os.mkdir('one')

        with tdir():
            Path('one.txt').write_text('ONE')
            assert os.getcwd() != os.path.join(cwd, 'one')

        assert not Path('one/one.txt').exists()

        with tdir(use_dir='one'):
            Path('one.txt').write_text('ONE')
            assert os.getcwd() == os.path.join(cwd, 'one')

        assert Path('one/one.txt').read_text() == 'ONE'

    def test_save(self):
        with tdir(save=True) as td:
            Path('one.txt').write_text('ONE')

        assert Path(os.path.join(td, 'one.txt')).read_text() == 'ONE'
        shutil.rmtree(td)

    def test_copy_dir(self):
        root = Path(__file__).parent
        with tdir(root=root) as td:
            copied = sorted(f.name for f in (td / 'root').iterdir())
            original = sorted(f.name for f in root.iterdir())
            assert copied == original


class TestBig(unittest.TestCase):
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
    def test_not_in_root0(self):
        cwd = str(Path().absolute())
        assert cwd != CWD

    def test_not_in_root1(self):
        @tdir
        def fn():
            cwd = str(Path().absolute())
            assert cwd != CWD

        fn()

    @tdir()
    def test_not_in_root2(self):
        cwd = str(Path().absolute())
        assert cwd != CWD

    @tdir('a', foo='bar')
    def test_values(self):
        assert Path('a').read_text() == 'a\n'
        assert Path('foo').read_text() == 'bar\n'


@tdir('a', foo='bar', methods='test_keep')
class TestTdirClassMethods(unittest.TestCase):
    def test_keep(self):
        cwd = Path().absolute()
        assert cwd != CWD

    def test_not(self):
        cwd = Path().absolute()
        assert cwd == CWD


class TestRecursive(unittest.TestCase):
    def test_recursive(self):
        d1 = Path().absolute()
        with tdir() as d2:
            f2 = d2 / 'one.txt'
            f2.write_text('one.txt')

            with tdir() as d3:
                f3 = d3 / 'two.txt'
                f3.write_text('two.txt')
                assert all(p.is_absolute() for p in (d1, d2, d3))
                assert d1 != d2 != d3 != d1
                assert f2.exists() and f3.exists()
            assert f2.exists() and not f3.exists()
        assert not f2.exists() and not f3.exists()
