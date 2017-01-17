#!/bin/bash
set -e

cd /src/ptools
python setup.py build && python setup.py install

if [[ $@ == "test" ]]
then
    cd Tests && make unittests
else
    exec "bash"
fi

