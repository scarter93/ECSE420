#include "lodepng.h"
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <sys/time.h>
#include <math.h>
#define THRESHOLD 200

//int results*;
unsigned char *image, *new_image;
unsigned width = 0, height = 0;

void *worker_thread(void *arg) {
  int *pos_val = (int*)arg;
  int value;
  fprintf(stdout, "first width = %d\nsecond width = %d\nfirst height =  %d\nsecond height = %d\n", pos_val[0], pos_val[1], pos_val[2], pos_val[3]);
  for (int i = pos_val[0]; i < pos_val[1]; i++) {
    for (int j = pos_val[2]; j < pos_val[3]; j++) {

      int check = image[4*width*i + 4*j];
      value = check <= THRESHOLD ? 0 : 255;

      new_image[4*width*i + 4*j] = value;
      new_image[4*width*i + 4*j + 1] = value;
      new_image[4*width*i + 4*j + 2] = value;
      new_image[4*width*i + 4*j + 3] = 255;
    }
  }
  //pthread_exit(NULL);
}

void binarize(char* input_filename, char* output_filename, int thread_count)
{
  unsigned error;
  int pos[4];
  // load image from PNG into C array
  error = lodepng_decode32_file(&image, &width, &height, input_filename);
  if(error) printf("error %u: %s\n", error, lodepng_error_text(error));
  new_image = malloc(width * height * 4 * sizeof(unsigned char));

  struct timeval start, end; // struct used to compute execution time
  gettimeofday(&start, NULL);  // set starting point
  for(int k = 0; k < 4; k++) pos[k] = 0;

  int width_piece = (int)(lround(width/thread_count));
  //int height_init = 0;
  int height_piece = (int)(lround(height/thread_count));

  /* TODO: create your thread team here and send each thread an argument
  telling it which part of "image" to process
  remember to join all threads!
  */
  //results = malloc(width * height * 4 * sizeof(unsigned char));
  pthread_t threads[thread_count];
  for(int i = 0; i < thread_count; i++){
    if(pos[0] == 0 && pos[2] == 0)
      pos[1] = width_piece;
      pos[3] = height_piece;
    else {
      pos[0] += width_piece;
      pos[1] += width_piece;
      pos[2] += height_piece;
      pos[3] += height_piece;
    }
    int *j = malloc(2*sizeof(int));
    *j = pos;
    int c = pthread_create(&threads[i], NULL, &worker_thread, j);
    if (c != 0) {
      fprintf(stderr, "Error creating pthreads exiting...\n");
      exit(1);
    }
  }

  for(int i = 0; i < thread_count; i++) {
    int c = pthread_join(threads[i], NULL);
    if (c != 0) {
      fprintf(stderr, "Error joining pthreads exiting...\n");
      exit(1);
    }
  }

  gettimeofday(&end, NULL);
  printf("\n\nAlgorithm's computational part duration : %ld\n", \
               ((end.tv_sec * 1000000 + end.tv_usec) - (start.tv_sec * 1000000 + start.tv_usec)));


  lodepng_encode32_file(output_filename, new_image, width, height);

  free(image);
  free(new_image);
  //free(result);
  free(threads)
}

int main(int argc, char *argv[])
{
  char* input_filename = argv[1];
  char* output_filename = argv[2];
  int thread_count = atoi(argv[3]);

  binarize(input_filename, output_filename, thread_count);

  return 0;
}
