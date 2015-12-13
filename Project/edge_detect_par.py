import png
import threading as thread
import math
import time
import numpy as np
import scipy as sp
from scipy import signal

num_threads = 4
threads = [None] * num_threads
mutex = thread.Lock()
barrier = thread.Barrier(4)
image_blur = []
image_newX = []
image_newY = []
image_angle = []
image_out = []
out = []
step1 = []
step2 = []
sobel_filterX = np.array([[-1,0,1],[-2,0,2],[-1,0,1]])
sobel_filterY = np.array([[-1,-2,-1],[0,0,0],[1,2,1]])
max = 125
min_val = 50
def main():
    global out, image_blur, image_newX, image_newY, image_out, image_angle, step1, step2
    file_out = open('out_edge_sup_par.png', 'wb')
    reader = png.Reader('grayscale.png')
    image_info = reader.read()
    image = list(image_info[2])

    image_2d = np.vstack(map(np.uint16, image))
    image_blur = np.zeros(image_2d.shape)
    out = np.zeros(image_2d.shape)
    image_newX = np.zeros(image_2d.shape)
    image_newY = np.zeros(image_2d.shape)
    image_out = np.zeros(image_2d.shape)
    image_angle = np.zeros(image_2d.shape)
    step1 = np.zeros(image_2d.shape)
    step2 = np.zeros(image_2d.shape)

    #if image_info[3]['greyscale'] != True or image_out[3]['alpha'] != False:
    #    print("please enter an image in greyscale and without alpha data")
    #    exit(1);

    start_threads(image_2d)
    end_threads()

    out = png.Writer(image_info[0], image_info[1], **image_info[3])
    out.write(file_out, image_out)
    file_out.close()

def start_threads(image):
    piece = math.ceil((len(image)/4))
    for i in range(num_threads):
        start = i*piece
        stop = int(min((i+1)*piece, len(image)))
        threads[i] = thread.Thread(target=worker, args=(image,start,stop))
        threads[i].daemon = True
        threads[i].start()

def end_threads():
    for i in range(num_threads):
        threads[i].join()

def min(X,Y):
    return X if X < Y else Y

def worker(image_2d, rows_start, rows_stop):
    create_blur(image_2d, rows_start, rows_stop)
    barrier.wait()

    create_gradients(rows_start, rows_stop)
    non_max_suppression(rows_start, rows_stop)
    hysteresis(rows_start, rows_stop)

def convolve(matrix, kernel, rows_start, rows_stop,out):
    k_centerX = int(len(kernel)/2)
    k_centerY = int(len(kernel[0])/2)

    k_rows = len(kernel)
    k_cols = len(kernel[0])

    in_rows = len(matrix)
    in_cols = len(matrix[0])

    for i in range(in_rows):
        #check to see if working on my section
        if rows_start > i:
            continue
        elif rows_stop <= i:
            return
        else:
            for j in range(in_cols):
                for m in range(k_rows):
                    #row index of flipped kernel
                    ri_flipped = k_rows - 1 - m
                    for n in range(k_cols):
                        #column index of flipped kernel
                        ci_flipped = k_cols - 1 -n
                        #index of input signal, used for checking bounds
                        i_index = i + (m - k_centerY)
                        j_index = j + (n - k_centerX)

                        #ignore invalid input samples
                        if (i_index >= 0 and i_index < in_rows) and (j_index >= 0 and j_index < in_cols):
                            out[i,j] += matrix[i_index,j_index] * kernel[ri_flipped, ci_flipped]

def create_blur(image_2d, rows_start, rows_stop):
    global image_blur, out
    kernelX = np.array([[1],[4],[6],[4],[1]])
    kernelY = np.array([[1,4,6,4,1]])

    convolve(image_2d, kernelX, rows_start, rows_stop, step1)
    barrier.wait()

    convolve(step1, kernelY, rows_start, rows_stop, step2)
    for i in range(rows_start, rows_stop):
        image_blur[i] = step2[i]/256

def create_gradients(rows_start, rows_stop):
    global image_newX, image_newY, image_out, out
    convolve(image_blur, sobel_filterX, rows_start, rows_stop, image_newX)
    barrier.wait()

    convolve(image_blur, sobel_filterY, rows_start, rows_stop, image_newY)
    for i in range(rows_start, rows_stop):
        image_out[i] = np.sqrt(np.power(image_newX[i],2)+np.power(image_newY[i], 2))
    create_angles(rows_start,rows_stop)


def create_angles(rows_start, rows_stop):
    global image_angle
    for i in range(rows_start, rows_stop):
        image_angle[i] = np.rad2deg(np.arctan2(image_newY[i], image_newX[i]))

def hysteresis(rows_start, rows_stop):
    global image_out

    for i in range(len(image_out)):
        if rows_start > i:
            continue
        if rows_stop <= i:
            return
        for j in range(len(image_out[0])):
            if image_out[i,j] > max:
                image_out[i,j] = 255
            elif image_out[i,j] < min_val:
                image_out[i,j] = 0
            elif (i > 0 and i < (len(image_out)-1)) and (j > 0 and j < (len(image_out[0])-1)):
                if image_out[i,j + 1] > max or image_out[i,j -1] > max or image_out[i + 1,j] > max or image_out[i - 1,j] > max:
                    image_out[i,j] = 255
                elif image_out[i + 1,j + 1] > max or image_out[i + 1,j -1] > max or image_out[i - 1,j + 1] > max or image_out[i - 1,j - 1] > max:
                    image_out[i,j] = 255
                else:
                    image_out[i,j] = 0
def non_max_suppression(rows_start, rows_stop):
    global image_out
    for i in range(1,len(image_out)-1):
        if rows_start > i:
            continue
        if rows_stop <= i:
            return
        for j in range(1,len(image_out)-1):
            if ((-22.5 < image_angle[i,j]) and (image_angle[i,j] <= 22.5)) or ((157.5 < image_angle[i,j]) and (image_angle[i,j] <= -157.5)):
                if ((image_out[i, j] < image_out[i, j + 1]) or (image_out[i, j] < image_out[i, j - 1])):
                    image_out[i, j] = 0
            #Vertical Edge
            if (((-112.5 < image_angle[i,j]) and (image_angle[i,j] <= -67.5)) or ((67.5 < image_angle[i,j]) and (image_angle[i,j] <= 112.5))):
                if ((image_out[i, j] < image_out[i + 1, j]) or (image_out[i, j] < image_out[i - 1, j])):
                    image_out[i, j] = 0
            #+45 Degree Edge
            if (((-67.5 < image_angle[i,j]) and (image_angle[i,j] <= -22.5)) or ((112.5 < image_angle[i,j]) and (image_angle[i,j] <= 157.5))):
                if ((image_out[i, j] < image_out[i + 1, j - 1]) or (image_out[i, j] < image_out[i - 1, j + 1])):
                    image_out[i, j] = 0
            #-45 Degree Edge
            if (((-157.5 < image_angle[i,j]) and (image_angle[i,j] <= -112.5)) or ((67.5 < image_angle[i,j]) and (image_angle[i,j] <= 22.5))):
                if ((image_out[i, j] < image_out[i + 1, j + 1]) or (image_out[i, j] < image_out[i - 1, j - 1])):
                    image_out[i, j] = 0;

if __name__ == "__main__":
    start_time = time.time()
    main()
    print("execution time: " + str(time.time() - start_time))
