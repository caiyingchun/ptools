#!/bin/bash
set -e

cd /src/ptools

if [[ $@ == "test" ]]
then
    make clean && make install && make test
else
    exec "bash"
fi

