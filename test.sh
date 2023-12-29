#!/bin/bash

set -eux

mypy tdir
isort tdir test_tdir.py
black tdir test_tdir.py
ruff check --fix tdir test_tdir.py
coverage run $(which pytest)
coverage html
