test: wrap.cpp chrg_scorpion.f
	gfortran chrg_scorpion.f -c
	gcc wrap.cpp -c -lstdc++
	gcc -o test wrap.o chrg_scorpion.o /usr/lib/x86_64-linux-gnu/libgfortran.so.3 -lstdc++ -lm

run:
	./test
