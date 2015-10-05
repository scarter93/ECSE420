#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

int main(int argc, char ** argv) {
  int A,B,C,D;
  int op1, op2, op3;
  int rank = 4;
  printf("rank = %d\n", rank);
  MPI_Init(&argc, &argv);
  MPI_Status status;
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  //MPI_Bcast(&A, sizeof(A)/sizeof(int), MPI_INT, 0, MPI_COMM_WORLD);

  if (rank == 3) {
    MPI_Bcast(&A, sizeof(A)/sizeof(int), MPI_INT, 0, MPI_COMM_WORLD);
    op3 = (A-1)*(A-2);
    MPI_Send(&op3, sizeof(op1)/sizeof(int), MPI_INT, 0, 3, MPI_COMM_WORLD);
  } else if(rank == 1) {
    B = atoi(argv[1]);
    printf("B = %d\n", B);
    MPI_Bcast(&A, sizeof(A)/sizeof(int), MPI_INT, 0, MPI_COMM_WORLD);
    op1 = A*B;
    MPI_Send(&B, sizeof(B)/sizeof(int), MPI_INT, 2, 1, MPI_COMM_WORLD);
    MPI_Send(&op1, sizeof(op1)/sizeof(int), MPI_INT, 0, 1, MPI_COMM_WORLD);
  } else if(rank == 2) {
    C = atoi(argv[2]);
    printf("C = %d\n", C);
    MPI_Recv(&B, sizeof(B)/sizeof(int), MPI_INT, 1, 1, MPI_COMM_WORLD, &status);
    MPI_Bcast(&A, sizeof(A)/sizeof(int), MPI_INT, 0, MPI_COMM_WORLD);
    op2 = B/(A+C);
    MPI_Send(&op2, sizeof(op2)/sizeof(int), MPI_INT, 0, 2, MPI_COMM_WORLD);
  } else if(rank == 0) {
    A = atoi(argv[0]);
    printf("A = %d\n", A);
    MPI_Bcast(&A, sizeof(A)/sizeof(int), MPI_INT, 0, MPI_COMM_WORLD);

    MPI_Recv(&op3, sizeof(op3)/sizeof(int), MPI_INT, 3, 3, MPI_COMM_WORLD, &status);
    MPI_Recv(&op2, sizeof(op2)/sizeof(int), MPI_INT, 2, 2, MPI_COMM_WORLD, &status);
    MPI_Recv(&op1, sizeof(op1)/sizeof(int), MPI_INT, 1, 1, MPI_COMM_WORLD, &status);
    D = op1 + op2 + op3;
    printf("D = %d\n", D);
  }

  MPI_Finalize();
}
