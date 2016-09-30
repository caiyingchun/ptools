

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
	python test_atom.py -v
	python test_atomselection.py -v
	python test_attractrigidbody.py -v
	python test_attractforcefield.py -v
	python test_basepair.py -v
	python test_coord3d.py -v
	python test_coordsarray.py -v
	python test_dna.py -v
	python test_movement.py -v
	python test_rigidbody.py -v
	python test_superpose.py -v
	python test_attractforcefield.py -v
	cd heligeom && python test_heligeom.py -v
	python unittest1.py


testcpp:
	echo "running C++ tests"
	python cxxtestgen.py --error-printer ptoolstest.h > runner.cpp
	g++ -O2 runner.cpp -I../headers -I. -L.. -lptools -o ptoolstest.bin
	./ptoolstest.bin

