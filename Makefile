

help:
	@echo "usage: make <command>"
	@echo ""
	@echo "Available commands:"
	@echo "    help - show this help"
	@echo "    clean - remove all build, test, coverage and Python artifacts"
	@echo "    clean-build - remove all build artifacts"
	@echo "    clean-pyc - remove all Python artifacts"
	@echo "    clean-pyc - remove test and coverage artifacts"


clean: clean-build clean-pyc clean-test


clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +


clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +


clean-test:
	rm -f Tests/cpp/runner.cpp
	rm -f Tests/cpp/ptoolstest.bin
	rm -rf .cache