#!/bin/bash
set -e

cd /src/ptools
python setup.py build && python setup.py install

cd Tests
make

exec "$@"
