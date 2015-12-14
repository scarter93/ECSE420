import sys              ##Sys calls
import numpy as np      ##NumPy since its great
import time             ##Not used, should be able to be removed
from mpi4py import MPI  ##MPI 

EPSILON = .000001       ##For zero adjusting

##Set up global COMM variable and RANK, NUM_PROC info
COMM = MPI.COMM_WORLD
NUM_PROC = COMM.Get_size()
RANK = COMM.Get_rank()

def main(argv): ##MAIN
    #If no file, please re-enter
    if len(argv) == 1:
        print("Error please enter a file")
        exit(0)
    #If # processes is only 1 please re-enter
    #TODO: function with a single process
    if NUM_PROC == 1:
        print("please enter a number of processes greater than 1")
        sys.exit(0)
    #Get matrix
    matrix_rows, matrix = read_user_matrix_from_file(argv[1])
    #Wait for everyone
    COMM.Barrier()
    #Reduce
    RREF(matrix, matrix_rows)
    #Wait for everyone
    COMM.Barrier()
    #Divide my max
    divide_by_max(matrix, matrix_rows)
    #Wait for everyone
    COMM.Barrier()
    #Write to file
    #TODO: Remove hardcode
    write_clicking_probabilities(matrix, matrix_rows, "output_clicking_probabilties_mpi.txt")
    #Wait for everyone
    COMM.Barrier()

 ##UNCOMMENT TO FOR Question 1.4 (get best threshold)

    acceptance_thres(matrix, matrix_rows)
    COMM.Barrier()
##
#This function sends the probabilties to the root
#The Root then writes to the file
#The writing part is fully sequential (done by root)
#But sending the matrix to zero to done in parallel
#TODO: make writing fully parallel
##
def write_clicking_probabilities(matrix,rows, filename):
    #open file to write to
    file = open(filename, "w")
    #if Process has no data then write nothing
    if RANK > NUM_PROC-1:
        return;
    #Root process revs matrix and writes the clicking probs
    if RANK == 0:
        cols = len(matrix[0,])
        row_total = cols-1
        #get correct chunksize
        if(NUM_PROC >= row_total):
            chunk_size = 1
            diff = 0
        else:
            diff = (row_total % NUM_PROC)
            chunk_size = np.floor(row_total/NUM_PROC)
        next = np.zeros((chunk_size, cols))
        #write root values first
        for row in range(int(rows)):
            print("%f" % matrix[row,cols-1], end= " ", file=file)
        #write all other values in order
        for i in range(1, NUM_PROC):
            COMM.Recv(next, source=i)
            for j in range(int(next.shape[0])):
                print("%f" %next[j,cols-1], end= " ", file=file)
    #everyone else send data to root
    elif RANK < NUM_PROC:
        COMM.Send(matrix, dest=0)
    #close file
    file.close()

##
#This function perfomrs Gaussian elimination and back subsitution
#
#STEPS:(Gaussian elimination) (starts at top sends at bottom) 
#   1. Perform gaussian elimination your section USING data from ABOVE you
#   2. Perform gaussian elimination on your internal matrix section
#   3. Normalize and send your data to processes/sections BELOW you
#
#STEPS: (Back Subsitution) (starts at bottom ends at top)
#   1. Back subsituted your internal matrix section
#   2. Back substiuted your section USING data from BELOW you
#   3. Send this data ABOVE you for rest of matrix
#
#Processes only take data from another when needed and do not store this data for later use
#The result is each process has its matrix sec/rows in RREF
#TODO: This is complex and could use some optimization and tweaking
##
def RREF(matrix, rows):
    #Setup for elimination
    global NUM_PROC
    if RANK == 0:
        cols = len(matrix[0,])
        row_total = cols- 1
    else:
        cols = None
        row_total = None
    cols = COMM.bcast(cols, root=0)
    row_total = COMM.bcast(row_total, root=0)
    #ajust NUM_PROC to make sure extra processes do nothing, they will skip this function

    ##
    ##
    #PLEASE READ: PLEASE READ:
    if(NUM_PROC > row_total):
        NUM_PROC = row_total
    #This performs a PERMANENT change to the global value NUM_PROC
    #This is done to adjust NUM_PROC to its "real" value
    #Meaning that all extra processes will be not counted as "real"
    #TODO: make this change less permanent use a different value
    ##
    ##

    #get chunk size(num rows) and the remaider (stored in rank 0)
    if(NUM_PROC >= row_total):
        chunk_size = 1
        diff = 0
    else:
        diff = (row_total % NUM_PROC)
        chunk_size = np.floor(row_total/NUM_PROC)
    #Gaussian Elimination
    if RANK ==0:
        start = 0
        #perform Gaussian elimination on internal rows
        for row in range(int(rows)):
            for row2 in range(int(rows)):
                if row2 <= row: continue
                pivot = matrix[row2,row]/matrix[row,row]
                matrix[row2,:] = matrix[row2,:] - pivot*matrix[row,:]
        #normalize
        for k in range(int(rows)):
            matrix[k,:] = matrix[k,:]/matrix[k,k]
            for col in range(cols):
                matrix[k, col] = 0 if equals(matrix[k, col], 0) else matrix[k,col]
        #send your reduced section to everyone below you
        for i in range(1, NUM_PROC):
            COMM.Send(matrix, dest=i)
    elif RANK < NUM_PROC:
        #Perform gaussian elimination using data sent to you
        for i in range(RANK):
            start = -1
            stop = -1
            #Get chunk size of incoming data
            #and their "real rows" in original matrix
            if i == 0: 
                current_sec = np.zeros((chunk_size + diff, cols))
                start = 0
                stop = int(chunk_size+diff)
            else:
                current_sec = np.zeros((chunk_size, cols))
                start = int(chunk_size*i+diff)
                stop = int(start + chunk_size)
            #recv data
            COMM.Recv(current_sec, source = i)
            #Perform gaussian elimination
            for k in range(rows):
                l = start 
                for j in range(current_sec.shape[0]):
                    pivot = matrix[k,l]/float(current_sec[j,l])
                    matrix[k,:] = matrix[k,:] - pivot*current_sec[j,:]
                    l+= 1
                l = start
        #get "real row" numbers for your section
        start = int(chunk_size*RANK + diff)
        stop = int(start + chunk_size)
        #Perform Gaussian elimination on your rows using your rows (internal)
        l=start
        for k in range(rows):
            for j in range(rows):
                if k >= j: continue
                pivot = matrix[j,l]/matrix[k,l]
                matrix[j,:] = matrix[j,:] - pivot*matrix[k,:]
            l += 1
        #adjust for almost zeros
        for k in range(int(rows)):
            for col in range(cols):
                matrix[k, col] = 0 if equals(matrix[k, col], 0) else matrix[k,col]
        #normalize
        l = start
        for entry in range(rows):
            matrix[entry,:] = matrix[entry,:] / matrix[entry,l]
            l += 1
        #send down
        for i in range(RANK+1, NUM_PROC):
            COMM.Send(matrix, dest=i)
    #wait for everyone to complete Gaussian elimination
    COMM.Barrier()
    #perform back subsitution
    if RANK == NUM_PROC-1:
        #perform internal back subsitution
        l=row_total-1
        for k in range(int(rows)-1, -1, -1):
            for j in range(int(rows)-1, -1, -1):
                if k <= j: continue
                pivot = matrix[j,l]/matrix[k,l]
                matrix[j,:] = matrix[j,:] - pivot*matrix[k,:]
            l-= 1
        #send data back up
        for i in range(RANK-1, -1, -1):
            COMM.Send(matrix, dest=i)
    elif RANK < NUM_PROC:
        rows = int(rows)
        #perform internal back subsitution
        start = int(chunk_size*RANK + diff)
        stop = int(start + chunk_size)
        l= stop-1
        for k in range(rows-1, -1, -1):
            for j in range(rows-1, -1, -1):
                if k <= j: continue
                pivot = matrix[j,l]/matrix[k,l]
                matrix[j,:] = matrix[j,:] - pivot*matrix[k,:]
            l-= 1
        #perform back subsitution for all incoming sections
        for i in range(NUM_PROC-1, RANK,-1):
            #get correct chunksize for incoming data
            if i == 0: 
                current_sec = np.zeros((chunk_size + diff, cols))
                start = 0
                stop = int(chunk_size+diff)
            else:
                current_sec = np.zeros((chunk_size, cols))
                start = int(chunk_size*i+diff)
                stop = int(start + chunk_size)
            #recv data
            COMM.Recv(current_sec, source = i)
            #perfrom back sub
            for k in range(rows-1, -1,-1):
                l = stop-1
                for j in range(current_sec.shape[0]-1, -1, -1):
                    pivot = matrix[k,l]/current_sec[j,l]
                    matrix[k,l:] = matrix[k,l:] - pivot*current_sec[j,l:]
                    l-= 1
                l = stop-1
        #send upward
        for i in range(RANK-1, -1, -1):
            COMM.Send(matrix, dest=i)
    #wait for all to finish
    COMM.Barrier()

##
#This function finds the max and divides by it.
#Starting at the root each process calculates it max value and 
#passes it along if it greater than max from row above
#Once this is completed and reaches the highest RANKed process with data 
#divide and send max back to every so they can divide by max
#TODO: This could use some improvement since it is rather complex.
##
def divide_by_max(matrix, rows):
    if RANK == 0:
        max = 0
        cols = len(matrix[0,])
        #get max so we can use this to divide
        for row in range(int(rows)):
            max = abs(matrix[row,cols-1]) if max < abs(matrix[row,cols-1]) else max
        #pass max forward
        COMM.send(max, dest = 1)
    elif RANK < (NUM_PROC-1):
        max = 0
        cols = len(matrix[0,])
        for row in range(int(rows)):
            #find max
            max = abs(matrix[row,cols-1]) if max < abs(matrix[row,cols-1]) else max
        #compare
        next_max = COMM.recv(source=(RANK-1))
        if max < next_max:
            max = next_max
        #pass max along
        COMM.send(max, dest=(RANK+1))
    elif RANK == (NUM_PROC-1):
        max = 0
        cols = len(matrix[0,])
        for row in range(int(rows)):
            #find max
            max = abs(matrix[row,cols-1]) if max < abs(matrix[row,cols-1]) else max
        next_max = COMM.recv(source=(RANK-1))
        #compare
        if max < next_max:
            max = next_max
        #send it back
        for i in range(RANK-1,-1,-1):
            COMM.send(max, dest=i)
        #divide by max
        for row in range(int(rows)):
            matrix[row,cols-1] = 0.0 if equals(max,0) else (abs(matrix[row,cols-1]) / max)
    if RANK < (NUM_PROC-1):
        #recv real max
        max = COMM.recv(source=NUM_PROC-1)
        #divide by max
        for row in range(int(rows)):
            matrix[row,cols-1] = 0.0 if equals(max,0) else (abs(matrix[row,cols-1]) / max)

def equals(a, b):   #return bool
    return True if abs(a-b) < EPSILON else False
##
#This functions read from the file
#This is done in parallel
#There is some overhead in my implementation (currently)
#Since the root process opens a second copy of the file just to get the row #'s
#ALL reading is done in parallel besides overhead
#TODO: optimize to minimize overhead
##
def read_user_matrix_from_file(filename): #return num_rows, matrix
    #open two files, one for findings rows/cols one for reading
    file = open(filename, 'r')          
    file2 = open(filename, 'r')
    #sent up data         
    num_rows = 0
    num_cols = 0
    #root finds info and bcasts it
    if RANK == 0:                           
        num_rows = sum(1 for line in file)
        num_cols = num_rows + 1
        if( NUM_PROC > num_rows):
            chunk_size = 1
            diff = 0
        else:
            diff = (num_rows % NUM_PROC)
            chunk_size = np.floor(num_rows/NUM_PROC)
    #set up vars for other processes
    else:
        chunk_size = None                   
        diff = None
        num_cols = None
    #bcast info
    diff = COMM.bcast(diff, root=0)         
    chunk_size = COMM.bcast(chunk_size, root=0)
    num_cols = COMM.bcast(num_cols, root=0) 
    #wait for everyone to recv
    COMM.Barrier()
    #if more processes than rows dont read data from file
    if (RANK >= num_cols-1):                
        return None, None
    #Reads data in parallel, slightly differen for root hence RANK == 0
    if RANK == 0:
        matrix = np.zeros((chunk_size+diff, num_cols), dtype = np.float64)
        row = 0
        for line in file2:
            if row < (chunk_size+diff):
                enteries = list(map(float, line.split()))
                for col in range(num_cols):
                    matrix[row, col] = enteries[col]
            row += 1;
        return chunk_size+diff, matrix
    #other processes read selected data
    else:
        if RANK >= num_cols-1: 
            return None, None
        next_matrix = np.zeros((chunk_size, num_cols), dtype = np.float64)
        real_row = 0
        row = 0
        for line in file2:
            if row < chunk_size*RANK + diff:
                row += 1
            elif real_row < chunk_size:
                entries = list(map(float, line.split(' ')))
                for col in range(num_cols):
                    next_matrix[real_row, col] = entries[col]
                real_row += 1
        return int(chunk_size), next_matrix
    #close files on completion
    file.close()
    file2.close()

def acceptance_thres(matrix, rows):     #prints the most profitable result for I <3 cats
    #number of threshold valus
    thres_num = 5                       
    all_entry = np.zeros(thres_num)
    entry = np.zeros(thres_num)
    #if process acually has data do calculations
    if RANK < NUM_PROC:                 
        cols = len(matrix[0,])
         #calculate threshold increment
        thres = 1/thres_num            
        for j in range(thres_num):
            for i in range(int(rows)):
                if matrix[i,cols-1] > thres:
                    entry[j] += matrix[i,cols-1]
                    entry[j] -= 2*(1-matrix[i,cols-1])
            thres += (1/thres_num)
        COMM.Reduce(entry,all_entry, root=0)
        #if process is root calculate the best threshold
        if RANK == 0:                  
            thres_val = 1/thres_num
            max = 0
            out = 0
            for i in range(thres_num):
                if all_entry[i] > max:
                    max = all_entry[i]
                    out = thres_val*(i+1)
            print(out)
    #if no data send zeros to reduce
    else:
        COMM.Reduce(entry,all_entry, root=0)    

if __name__ == "__main__":     #execute main function
##UNCOMMENT FOR TIMING
    #start_time = MPI.Wtime()                    
    main(sys.argv)
##UNCOMMENT FOR TIMING                               
    #file = open("time_results_mpi.txt", "a")     
    #print("%f" %(MPI.Wtime() - start_time), file=file)
    #file.close()                                      