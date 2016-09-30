
# !!! TO-DO: add testcpp in testing process
unittests: testpython

testpython:
	echo "running python tests"
	python unittest1.py
	python test_dna.py -v
	python test_basepair.py -v
	python test_movement.py -v
	cd heligeom && python heligeom_test.py -v

testcpp:
	echo "running C++ tests"
	python cxxtestgen.py --error-printer ptoolstest.h > runner.cpp
	g++ -O2 runner.cpp -I../headers -I. -L.. -lptools -o ptoolstest.bin
	./ptoolstest.bin

