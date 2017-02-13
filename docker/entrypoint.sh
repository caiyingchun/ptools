#!/bin/bash
set -e

cd /src/ptools
make install

if [[ $@ == "test" ]]
then
    make test
else
    exec "bash"
fi

