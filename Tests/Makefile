

help:
	@echo "Usage: make <command>"
	@echo "Available commands:"
	@echo "    help - print this help"
	@echo "    unittests - run Python and C++ tests (!!! C++ tests disabled right now)"
	@echo "    testpython - run Python tests"
	@echo "    testcpp - run C++ tests"


# !!! TO-DO: add testcpp in testing process
unittests: testpython


testpython:
	echo "running python tests"
	py.test -v

testcpp:
	echo "running C++ tests"
	python cxxtestgen.py --error-printer ptoolstest.h > runner.cpp
	g++ -O2 runner.cpp -I../headers -I. -L.. -lptools -o ptoolstest.bin
	./ptoolstest.bin
