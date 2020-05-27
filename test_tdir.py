from tdir import tdir
import sys
import unittest


class TestTdir(unittest.TestCase):
    def test_simple(self):
        with tdir('a', 'b', 'c') as td:
            assert sorted(i.name for i in td.iterdir()) == ['a', 'b', 'c']
            for i in 'abc':
                assert (td / i).read_text() == i + '\n'

    def test_dict(self):
        with tdir(one='ONE', two='TWO') as td:
            assert sorted(i.name for i in td.iterdir()) == ['one', 'two']
            for i in ('one', 'two'):
                assert (td / i).read_text() == i.upper() + '\n'

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
