import sys
import numpy as np
import time
from mpi4py import MPI

EPSILON = .000001

def main(argv):
    if len(argv) == 1:
        print("Error please enter a file")
        exit(0)

    rows, cols, input_matrix = read_user_matrix_from_file(argv[1])
    cp_out = np.zeros(rows)
    #print(input_matrix)
    RREF(input_matrix, rows, cols)
    #print(input_matrix)
    divide_by_max(input_matrix, rows, cols)
    input_clicking_probabilities(input_matrix, rows, cols, cp_out)
    #print(cp_out)
    write_clicking_probabilities(cp_out, rows, "clicking_probs_seq_test.txt")

def input_clicking_probabilities(matrix, rows, cols, cp):
    for row in range(rows):
        cp[row] = matrix[row,cols-1]

def write_clicking_probabilities(cp, rows, filename):
    file = open(filename, "w")
    for row in range(rows):
        print("%f" %cp[row], end= " ", file=file)
    file.close()

def RREF(matrix, rows, cols):
    #Gaussian elimination
    for src_row in range(rows):
        for dest_row in range(rows):
            if (dest_row == src_row):
                continue
            pivot = matrix[dest_row,src_row] / matrix[src_row,src_row]
            #print(pivot)
            for col in range(src_row, cols):
                matrix[dest_row,col] = matrix[dest_row,col] - pivot*matrix[src_row,col]
    #Back-substitution
    for row in range(rows-1, -1, -1):
        matrix[row,cols-1] = matrix[row,cols-1] / matrix[row,row]
        matrix[row,row] = 1
    #get almost zeros to zeros
    for row in range(rows):
        for col in range(cols):
            matrix[row, col] = 0 if equals(matrix[row, col], 0) else matrix[row,col]

def divide_by_max(matrix, rows, cols):
    max = 0
    #get max so we can use this to divide
    for row in range(rows):
        max = abs(matrix[row,cols-1]) if max < abs(matrix[row,cols-1]) else max
    #divide by max and take abs...includes check for div-by-0
    for row in range(rows):
        matrix[row,cols-1] = 0.0 if equals(max,0) else (abs(matrix[row,cols-1]) / max)

def equals(a, b):   #return bool
    return True if abs(a-b) < EPSILON else False

def print_matrix(matrix, rows, cols):
    for row in range(rows):
        for col in range(cols):
            print("%f, " % matrix[row, col], end="")
        print("\n")

def read_user_matrix_from_file(filename): #return row,col,matrix
    file = open(filename, 'r')
    file2 = open(filename, 'r')
    check = False
    num_cols = 0
    num_rows = 0
    for line in file:

        if not(check):
            cols = list(map(float, line.split(' ')))
            num_cols = len(cols)
            check = True
        num_rows += 1
    
    #print(num_cols, num_rows)
    matrix = np.zeros((num_rows, num_cols))
    
    row = 0
    for line in file2:
        entries = list(map(float, line.split(' ')))
        for col in range(num_cols):
            matrix[row, col] = entries[col]
        row += 1
    
    file.close()
    file2.close()
    return num_rows, num_cols, matrix

if __name__ == "__main__":
    start_time = time.time()
    main(sys.argv)
    file = open("time_results_seq.txt", "a")
    print("%f" %(time.time() - start_time), file=file)