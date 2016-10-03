
PTOOLS_TEST_BIN = ptoolstest.bin
PTOOLS_TEST_SRC = runner.cpp


LIBPTOOLS=$(shell find ../build -name '*ptools.so')
LIBPYTHON=$(shell python -c 'import sys; print "python{}.{}".format(sys.version_info.major, sys.version_info.minor)')


help:
	@echo "Usage: make <command>"
	@echo ""
	@echo "Available commands:"
	@echo "    help - print this help"
	@echo "    unittests - run Python and C++ tests"
	@echo "    testpython - run Python tests"
	@echo "    testcpp - run C++ tests"
	@echo "    clean - remove all temporary files"
	@echo "    clean-python - remove python temporary files"
	@echo "    clean-cpp - remove C++ temporary files"

unittests: testcpp testpython


testpython:
	echo "running python tests"
	py.test -v

testcpp: $(PTOOLS_TEST_BIN)
	echo "running C++ tests"
	./$^

$(PTOOLS_TEST_BIN): $(PTOOLS_TEST_SRC)
	g++ -O2 -I. -I../headers -l$(LIBPYTHON) -o $@ $< $(LIBPTOOLS)

$(PTOOLS_TEST_SRC): ptoolstest.h
	python cxxtestgen.py --error-printer $< > $@

clean: clean-python clean-cpp

clean-python:
	rm -rf __pycache__

clean-cpp:
	rm -rf $(PTOOLS_TEST_SRC) $(PTOOLS_TEST_BIN)