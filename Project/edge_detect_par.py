import png      #image processing library for PNG
import math
import time
import numpy as np
import threading as thread
#set up  necessary primatives for algorithm
num_threads = 4
threads = [None] * num_threads
barrier = thread.Barrier(num_threads)
#initialize necessary global memory 
image_blur = []
image_newX = []
image_newY = []
image_angle = []
image_out = []
out = []
step1 = []
step2 = []
#constant sobel filters
sobel_filterX = np.array([[-1,0,1],[-2,0,2],[-1,0,1]])
sobel_filterY = np.array([[-1,-2,-1],[0,0,0],[1,2,1]])
#max and min values for hysteresis
max = 125
min_val = 50
def main():
    "main function, preforms execution of example code"
    global out, image_blur, image_newX, image_newY, image_out, image_angle, step1, step2
    #open the desired output, reader takes input TODO: give user option to enter file in and out
    file_out = open('out_edge_sup_par.png', 'wb')
    reader = png.Reader('grayscale.png')
    #get data from image
    image_info = reader.read()
    #format actual image from meta
    image = list(image_info[2])
    meta = image_info[3]
    #create all necessary image memory TODO: remove NumPy to increase efficiency
    image_2d = np.array(image)
    image_blur = np.zeros(image_2d.shape)
    out = np.zeros(image_2d.shape)
    image_newX = np.zeros(image_2d.shape)
    image_newY = np.zeros(image_2d.shape)
    image_out = np.zeros(image_2d.shape)
    image_angle = np.zeros(image_2d.shape)
    step1 = np.zeros(image_2d.shape)
    step2 = np.zeros(image_2d.shape)

    #TODO make sure user enters a true grayscale with no alpha
    if meta['greyscale'] != True or meta['alpha'] != False:
        print("please enter an image in greyscale and without alpha data")
        exit(1);
    #Start threads
    start_threads(image_2d)
    #Join threads on completion
    end_threads()
    #write to file
    out = png.Writer(image_info[0], image_info[1], **image_info[3])
    out.write(file_out, image_out)
    file_out.close()

def start_threads(image):
    "function that creates threads and assigns the portion of image"
    piece = math.ceil((len(image)/4))
    for i in range(num_threads):
        start = i*piece
        stop = int(min((i+1)*piece, len(image)))
        threads[i] = thread.Thread(target=worker, args=(image,start,stop))
        threads[i].daemon = True
        threads[i].start()

def end_threads():
    "joins threads on completion"
    for i in range(num_threads):
        threads[i].join()

def min(X,Y):
    "used to calculate minimum"
    return X if X < Y else Y

def worker(image_2d, rows_start, rows_stop):
    "function that does processing for each thread"
    #do gaussian blur
    create_blur(image_2d, rows_start, rows_stop)
    #wait for completion of all other threads
    barrier.wait()
    #create gradients and preform no-max-sup and hysteresis
    create_gradients(rows_start, rows_stop)
    non_max_suppression(rows_start, rows_stop)
    hysteresis(rows_start, rows_stop)

def convolve(matrix, kernel, rows_start, rows_stop,out):
    "function that convolves two matrices, built for a range of rows"
    #create necessary parameters for convolution
    k_centerX = int(len(kernel)/2)
    k_centerY = int(len(kernel[0])/2)
    k_rows = len(kernel)
    k_cols = len(kernel[0])
    in_rows = len(matrix)
    in_cols = len(matrix[0])
    #start the convolutions for section
    for i in range(rows_start, rows_stop):
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
    "uses convolve function to create gaussian blur"
    global image_blur, out
    #kernel used, it is separated which increases runtime
    kernelX = np.array([[1],[4],[6],[4],[1]])
    kernelY = np.array([[1,4,6,4,1]])
    factor = 256
    #perform firt convolution
    convolve(image_2d, kernelX, rows_start, rows_stop, step1)
    #wait for completion of all threads
    barrier.wait()
    #do second convolution and divide by factor
    convolve(step1, kernelY, rows_start, rows_stop, step2)
    for i in range(rows_start, rows_stop):
        image_blur[i] = step2[i]/factor

def create_gradients(rows_start, rows_stop):
    "this function creates the gradients in X and Y and magnitude"
    global image_newX, image_newY, image_out, out
    #find gradients in x direction
    convolve(image_blur, sobel_filterX, rows_start, rows_stop, image_newX)
    #wait for convolution to complete
    barrier.wait()
    #find gradients in the y direction
    convolve(image_blur, sobel_filterY, rows_start, rows_stop, image_newY)
    #create gradient magnitude array.
    for i in range(rows_start, rows_stop):
        image_out[i] = np.sqrt(np.power(image_newX[i],2)+np.power(image_newY[i], 2))
    create_angles(rows_start,rows_stop)

def create_angles(rows_start, rows_stop):
    "create the angles to perform non-max suppression"
    global image_angle
    for i in range(rows_start, rows_stop):
        image_angle[i] = np.rad2deg(np.arctan2(image_newY[i], image_newX[i]))

def hysteresis(rows_start, rows_stop):
    "performs hysteresis on image"
    global image_out
    for i in range(rows_start,rows_stop):
        #if range is acceptable set to max and min
        for j in range(len(image_out[0])):
            if image_out[i,j] > max:
                image_out[i,j] = 255
            elif image_out[i,j] < min_val:
                image_out[i,j] = 0
            #if image is connected to strong edge, it is an edge
            elif (i > 0 and i < (len(image_out)-1)) and (j > 0 and j < (len(image_out[0])-1)):
                if image_out[i,j + 1] > max or image_out[i,j -1] > max or image_out[i + 1,j] > max or image_out[i - 1,j] > max:
                    image_out[i,j] = 255
                elif image_out[i + 1,j + 1] > max or image_out[i + 1,j -1] > max or image_out[i - 1,j + 1] > max or image_out[i - 1,j - 1] > max:
                    image_out[i,j] = 255
                else:
                    image_out[i,j] = 0
def non_max_suppression(rows_start, rows_stop):
    "perform non max suppresion to remove weak edges"
    global image_out
    for i in range(rows_start+1, rows_stop-1):
        for j in range(1,len(image_out[0])-1):
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
    file = open('edge_time.csv', 'a')
    start_time = time.time()
    main()
    print(str(time.time() - start_time), file=file)
