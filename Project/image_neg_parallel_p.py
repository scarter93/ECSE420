import png
import threading as thread
import ctypes as c
import multiprocessing as mp
from multiprocessing import Pool
from functools import partial
import math
import time
import numpy as np


num_threads = 1
processes = [None] * num_threads
#new_image = []
the_image = []
image = []


def main():
    global image
    #global new_image
    reader = png.Reader('test.png')
    image_info = reader.read()
    image = list(image_info[2])
    n = len(image)
    print(n)
    m = len(image[0])
    print(m)
    
    #image = np.vstack(map(np.uint16, image))
    #new_image = np.zeros(image.shape)
    kkk = list()
    
    for i in range(n):
        kkk += list(image[i]) 

    the_image = mp.Array(c.c_double, kkk, lock=True)
    #print(the_image.shape)
    #for i in range(n):
    #    for j in range(m):
    #        the_image[i+j] = image[i][j]
            #print(str(image[i][j]) + " " + str(the_image[i,j]))
    print(the_image)
    
    ppp = [kkk[len(image[0])*(i) : len(image[0]*(i+1))] for i in range(0, len(image))]
    #ppp.append(kkk[len(image[0])*478 : len(image[0])*479])
    print(image[0])
    print("--")
    print(ppp[0])

    
    #for i,j in enumerate(the_image):
    #    print("[{0}] ppp == image: ".format(i) + str(ppp[i] == image[i]))


    results = list()
    pool = Pool(initializer=init, initargs=(the_image,), processes=num_threads)
    piece = math.ceil((len(image)/(num_threads)))
    for i in range(num_threads):
        start = int(i*piece)
        stop = int(min((i+1)*piece, len(image)))
        results += (pool.apply(worker, [start, stop]))


    #print(results)
    #start_threads(image)
    #end_threads()

    file_out = open('out_par_p.png', 'wb')
    out = png.Writer(image_info[0], image_info[1], **image_info[3])
    out.write(file_out, results)
    file_out.close()

def init(shared_arr):
    global the_image
    the_image = shared_arr

result_list = []
def log_result(result):
    # This is called whenever foo_pool(i) returns a result.
    # result_list is modified only by the main process, not the pool workers.
    result_list.append(result)

def worker(start, stop):
    global the_image
    test = list(the_image)
    #print(test)
    cols = int(400)
    #print("cols: " + str(cols))
    
    #print(mp.active_count())
    #global image
    #global new_image
    rows = stop-start
    print(start)
    print(stop)
    new_image = [[0]*(cols*4)]*rows
    entry = 0
    for row in range(start,stop):
        pixel = 0
        for i in range(int(cols)):
            new_image[row][pixel] = 255 - test[row*479 +pixel]
            new_image[row][pixel+1] = 255 - test[row*479 +pixel+1]
            new_image[row][pixel+2] = 255 - test[row*479 + pixel+2]
            new_image[row][pixel+3] = test[row*479 + pixel+3]
            pixel += 4
        entry += 1
    #print(new_image)
    return new_image

def test(x):
    return x*x

def start_threads(image):
    piece = math.ceil((len(image)/4))
    for i in range(num_threads):
        start = int(i*piece)
        stop = int(min((i+1)*piece, len(image)))
        processes[i] = Process(target=worker, args=(start, stop))
        processes[i].daemon = True
        processes[i].start()

def end_threads():
    for i in processes:
        i.join()

def min(X,Y):
    return X if X < Y else Y

if __name__ == "__main__":
    start_time = time.time()
    main()
    print("execution time: " + str(time.time() - start_time))
