#!/bin/bash

set -eux

mypy tdir.py
isort tdir.py test_tdir.py
black tdir.py test_tdir.py
ruff check --fix tdir.py test_tdir.py
coverage run $(which pytest)
coverage html
