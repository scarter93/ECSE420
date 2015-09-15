#include <stdio.h>
#include <pthread.h>
#include <stdlib.h>
#include <time.h>


void *init_rand(void *args);

static int *result;
static int num = 0;
pthread_mutex_t *check;

int main(int argc, char *argv[])
{
  srand(time(NULL));

  int N = atoi(argv[1]);
  int s;

  pthread_t thread[N];

  result = malloc(sizeof(int)*N);
  fprintf(stderr, "size: %d\n", sizeof(result));
  fprintf(stderr, "N = %d\n", N);

  pthread_mutex_init(check, NULL);

  int i;
  for (i = 0; i < N; i++)
  {
    s = pthread_create(&thread[i], NULL, &init_rand, &i);
    fprintf(stdout, "thread created \n");
    if (s != 0)
    {
      fprintf(stderr, "Error, exiting \n");
      exit(1);
    }
  }

  for (i = 0; i < N; i++)
  {
    s = pthread_join(thread[i], NULL);
    if (s != 0)
    {
      fprintf(stderr, "Error, exiting \n");
      exit(1);
    }
  }
  pthread_mutex_destroy(check);
  for (i = 0; i < N; i++)
  {
    if(i != (N-1))
      fprintf(stdout, "%d, ", result[i]);
    else
      fprintf(stdout, "%d", result[i]);
  }
}

void *init_rand(void *args)
{
  int r = rand() % 1000000;
  usleep(r);
  pthread_mutex_lock(check);
  result[num] = args;
  num++;
  pthread_mutex_unlock(check);
  return NULL;
}
