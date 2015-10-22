FOR /L %%A IN (1,1,100) DO (
mpiexec -n 4 python cp_mpi.py test_matrix.txt
)