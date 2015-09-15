#include <stdio.h>
#include <pthread.h>
#include <stdlib.h>
#include <time.h>


void *init_rand(void *args);

static int *Result;
static int num = 0;
pthread_mutex_t *check;

int main(int argc, char *argv[])
{
  srand(time(NULL));

  int N = atoi(argv[1]);

  pthread_t thread[N];
  Result = malloc(sizeof(int)*N);
  fprintf(stderr, "size: %d\n", sizeof(Result));
  fprintf(stderr, "N = %d\n", N);

  pthread_mutex_init(check, NULL);

  int i;
  for (i = 0; i < N; i++)
  {
    int s = pthread_create(&thread[i], NULL, &init_rand, &i);
    if (s != 0)
    {
      fprintf(stdout, "Error, exiting \n");
      exit(1);
    }
  }

  for (i = 0; i < N; i++)
  {
    int s = pthread_join(thread[i], NULL);
    if (s != 0)
    {
      fprintf(stdout, "Error, exiting \n");
      exit(1);
    }
  }
  pthread_mutex_destroy(check);
  for (i = 0; i < N; i++)
  {
    if(i != (N-1))
      fprintf(stdout, "%d, ", Result[i]);
    else
      fprintf(stdout, "%d", Result[i]);
  }
}

void *init_rand(void *args)
{
  int r = rand() % 1000000;
  usleep(r);
  pthread_mutex_lock(check);
  Result[num] = args;
  num++;
  pthread_mutex_unlock(check);
  return NULL;
}
