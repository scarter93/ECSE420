all: binarize_sequential binarize_pthreads binarize_openmp sobel_sequential sobel_openmp sobel_pthreads

binarize_sequential: binarize_sequential.o lodepng.o
		gcc -std=c99 -lm -o binarize_sequential binarize_sequential.o lodepng.o

binarize_pthreads: binarize_pthreads.o lodepng.o
		gcc -std=c99 -lm -pthread -o binarize_pthreads binarize_pthreads.o lodepng.o

binarize_openmp: binarize_openmp.o lodepng.o
		gcc -std=c99 -lm -fopenmp -o binarize_openmp binarize_openmp.o lodepng.o

binarize_sequential.o: binarize_sequential.c lodepng.h
		gcc -std=c99 -lm -c binarize_sequential.c

binarize_pthreads.o: binarize_pthreads.c lodepng.h
		gcc -std=c99 -lm -c -pthread binarize_pthreads.c

binarize_openmp.o: binarize_openmp.c lodepng.h
		gcc -std=c99 -lm -fopenmp -c binarize_openmp.c

sobel_sequential: sobel_sequential.o lodepng.o
		gcc -std=c99 -lm -o sobel_sequential sobel_sequential.o lodepng.o

sobel_pthreads: sobel_pthreads.o lodepng.o
		gcc -std=c99 -lm -pthread -o sobel_pthreads sobel_pthreads.o lodepng.o

sobel_openmp: sobel_openmp.o lodepng.o
		gcc -std=c99 -lm -fopenmp -o sobel_openmp sobel_openmp.o lodepng.o

sobel_sequential.o: sobel_sequential.c lodepng.h
		gcc -std=c99 -c sobel_sequential.c

sobel_pthreads.o: sobel_pthreads.c lodepng.h
		gcc -std=c99 -lm -c -pthread sobel_pthreads.c

sobel_openmp.o: sobel_openmp.c lodepng.h
		gcc -std=c99 -lm -fopenmp -c sobel_openmp.c

lodepng.o: lodepng.c lodepng.h
		gcc -std=c99 -lm -c lodepng.c

clean:
		rm *.o binarize_sequential binarize_openmp binarize_pthreads sobel_sequential sobel_openmp sobel_pthreads
