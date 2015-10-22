FOR /L %%A IN (1,1,100) DO (
mpiexec -n 2 python cp_mpi.py test_matrix.txt
)