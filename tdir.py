from pathlib import Path
import contextlib
import tempfile

__version__ = '0.9.0'


@contextlib.contextmanager
def tdir(*args, **kwargs):
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        fill(root, *args, **kwargs)
        yield root


def fill(root, *args, **kwargs):
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
