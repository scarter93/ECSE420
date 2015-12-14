import numpy as np
import sys
matrix = np.random.uniform(low=0.0, high=10.0,size=(200,201))
file = open("test_matrix.txt", 'w')
for i in range(matrix.shape[0]):
    for j in range(matrix.shape[1]):
        #matrix[i,j] = float(matrix[i,j])
        print("%.5f" % matrix[i,j], end = "", file=file)
        if j != 200:
            print(" ", end="", file=file)
    print("\n", end="", file=file)
file.close()
