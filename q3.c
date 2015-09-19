#include <stdio.h>
#include <pthread.h>
#include <stdlib.h>
#include <time.h>

void *init_rand(void *args);  //def functions

int *result;                  //def required global variables
int num = 0;
pthread_mutex_t *check;

int main(int argc, char *argv[]){
  if (argc != 2){              //check for cmd line entry error and exit
    fprintf(stderr, "argc = %d; exiting\n", argc);
    exit(1);
  }

  srand(time(NULL));          //seed random variables and def local variables
  int N = atoi(argv[1]);
  int s;
  pthread_t thread[N];

  result = malloc(sizeof(int)*N);           //allocate required memory
  check = malloc(sizeof(pthread_mutex_t));
  pthread_mutex_init(check, NULL);

  int i;
  for (i = 0; i < N; i++){              //create N pthreads and check for errors
    int *j = malloc(sizeof(int));
    *j = i;
    s = pthread_create(&thread[i], NULL, &init_rand, j);
    if (s != 0){
      fprintf(stderr, "Error, exiting \n");
      exit(1);
    }
  }
  for (i = 0; i < N; i++){            //join N pthreads and check for erros
    s = pthread_join(thread[i], NULL);
    if (s != 0){
      fprintf(stderr, "Error, exiting \n");
      exit(1);
    }
  }
  for (i = 0; i < N; i++){            //print results in order of completion
    if(i != (N-1))
      fprintf(stdout, "%d, ", result[i]);
    else
      fprintf(stdout, "%d\n", result[i]);
  }
  pthread_mutex_destroy(check);       //free up allocated memory
  free(result);
}

void *init_rand(void *args){      //function used by threads
  int r = rand() % 1000000;
  usleep(r);
  pthread_mutex_lock(check);      //lock mutex when changing shared memory
  result[num] = *((int*)args);
  free(args);
  num++;
  pthread_mutex_unlock(check);    //unlock mutex for next thread and return
  return NULL;
}
