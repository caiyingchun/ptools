.PHONY: help clean clean-build clean-pyc clean-test lint test docs 

# Docker image name.
DOCKER_IMAGE = ptools:dev

# File name in which installed files are recorded.
MANIFEST_OUT = MANIFEST.out

help:
	@echo "usage: make <command>"
	@echo ""
	@echo "Available commands:"
	@echo "    help - show this help"
	@echo "    clean - remove all build, test, coverage and Python artifacts"
	@echo "    clean-build - remove all build artifacts"
	@echo "    clean-pyc - remove all Python artifacts"
	@echo "    clean-test - remove test and coverage artifacts"
	@echo "    lint - check style with flake8"
	@echo "    test - run tests with default Python"
	@echo "    coverage - run tests and calculate coverage" 
	@echo "    docs - generate Sphinx HTML documentation"
	@echo "    build - build the package"
	@echo "    install - install the package to the active Python's site-packages"
	@echo "    docker-build - build a docker container for ptools"
	@echo "    docker-test - use the docker container ptools:dev to run unit tests"


clean: clean-build clean-pyc clean-test clean-docs


clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	rm -f bindings/_ptools.cpp
	rm -f bindings/_cgopt.cpp
	rm -f $(MANIFEST_OUT)
	rm -f headers/gitrev.h
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
	rm -f Tests/cpp/Makefile
	rm -f Tests/opt_scorpion.out
	rm -f Tests/iterate.dat
	rm -rf .cache
	rm -rf .coverage


clean-docs:
	rm -rf docs/_build


lint:
	flake8 --ignore=E501 tests
	flake8 --ignore=E501 --exclude=ptools/__init__.py ptools


test:
	$(MAKE) -C Tests

coverage:
	pytest --cov-report term-missing --cov=ptools Tests

docs:
	$(MAKE) -C docs clean
	$(MAKE) -C docs html


build: clean
	python setup.py build


install:
	python setup.py install --record $(MANIFEST_OUT)

undo:
	git checkout -- "*.py" "*.pyx" "*.cpp" "*.h"

rename:
	python names.py rename NAMES_TXN

uninstall:
	cat $(MANIFEST_OUT) | xargs rm -f 


docker-build:
	docker build -t $(DOCKER_IMAGE) ./docker


docker-test:
	docker run --rm -v $(shell pwd):/src/ptools $(DOCKER_IMAGE) test


docker-run:
	docker run --name ptools_interactive -it -v $(shell pwd):/src/ptools $(DOCKER_IMAGE)
	
