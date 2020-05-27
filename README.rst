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
