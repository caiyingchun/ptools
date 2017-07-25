# CHR This Makefile is just for developing the fortran wrapper in c++
test: test_wrap.cpp chrg_scorpion.f
	gfortran chrg_scorpion.f -c
	gcc test_wrap.cpp -c -lstdc++
	# Pick one:
	# -- for ubuntu linux
	#gcc -o test wrap.o chrg_scorpion.o /usr/lib/x86_64-linux-gnu/libgfortran.so.3 -lstdc++ -lm
	# -- for macports gfortran
	gcc -o test test_wrap.o chrg_scorpion.o /opt/local/lib/libgcc/libgfortran.3.dylib -lstdc++ -lm

run:
	./test
