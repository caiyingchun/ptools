
PTOOLS_TEST_BIN = ptoolstest.bin
PTOOLS_TEST_SRC = runner.cpp

LIBPTOOLS=$(shell find ../../build -name '*ptools.so')
LIBPYTHON=$(shell python -c 'import sys; print "python{}.{}".format(sys.version_info.major, sys.version_info.minor)')


all: unittests

help:
	@echo "Usage: make [command]"
	@echo ""
	@echo "Available commands:"
	@echo "    help - print this help"
	@echo "    unittests - run Python and C++ tests (default)"
	@echo "    clean - remove temporary files"

unittests: $(PTOOLS_TEST_BIN)
	echo "running C++ tests"
	./$^

$(PTOOLS_TEST_BIN): $(PTOOLS_TEST_SRC)
	g++ -O2 -I. -I../../headers -o $@ $< $(LIBPTOOLS) -l$(LIBPYTHON) 

$(PTOOLS_TEST_SRC): ptoolstest.h
	python cxxtestgen.py --error-printer $< > $@

clean:
	rm -rf $(PTOOLS_TEST_SRC) $(PTOOLS_TEST_BIN)