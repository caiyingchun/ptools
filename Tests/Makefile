

all: unittests

help:
	@echo "Usage: make <command>"
	@echo ""
	@echo "Available commands:"
	@echo "    help - print this help"
	@echo "    unittests - run Python and C++ tests"
	@echo "    testpython - run Python tests"
	@echo "    testcpp - run C++ tests"
	@echo "    clean - remove temporary files"
	@echo "    clean-python - remove python temporary files"
	@echo "    clean-cpp - remove C++ temporary files"

unittests: testcpp testpython


testpython:
	echo "running python tests"
	py.test -v

testcpp:
	$(MAKE) -C cpp unittests

clean: clean-python clean-cpp

clean-python:
	rm -rf __pycache__

clean-cpp:
	$(MAKE) -C cpp clean