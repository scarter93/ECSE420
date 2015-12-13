import png
import threading as thread
import math
import time
import numpy as np
import scipy as sp
from scipy import signal

image = []
image_new = []
image_newX = []
image_newY = []
image_angle = []
image_out = []
image_out_final = []
sobel_filterX = np.array([[-1,0,1],[-2,0,2],[-1,0,1]])
sobel_filterY = np.array([[-1,-2,-1],[0,0,0],[1,2,1]])
max = 125
min = 50
def main():
    global image
    global image_out_final
    file_out = open('out_edge_sup.png', 'wb')
    reader = png.Reader('grayscale.png')
    image_info = reader.read()
    image = list(image_info[2])
    #print (image_info)
    image_2d = np.vstack(map(np.uint16, image))

    #generate_filter(0.84089642, 7)
    #print(image)

    create_blur(image_2d)
    #print(image_new)
    create_gradients()
    #print(sobel_filterX)
    #print(sobel_filterY)
    create_angles()
    #print(image_angle)

    non_max_suppression()
    hysteresis()
    out = png.Writer(image_info[0], image_info[1], **image_info[3])
    out.write(file_out, image_out)
    file_out.close()

def convolve(matrix, kernel):
    out = np.zeros(matrix.shape)
    #print(matrix.shape)
    k_centerX = int(len(kernel)/2)
    k_centerY = int(len(kernel[0])/2)

    k_rows = len(kernel)
    k_cols = len(kernel[0])

    in_rows = len(matrix)
    in_cols = len(matrix[0])

    for i in range(in_rows):
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
    return out


def create_blur(image_2d):
    global image_new
    kernelX = np.array([[1],[4],[6],[4],[1]])
    kernelY = np.array([[1,4,6,4,1]])
    #kernel = np.array([[1,4,6,4,1],[4,16,24,16,4],[6,24,36,24,6],[4,16,24,16,4],[1,4,6,4,1]])
    #print(kernelX)
    #print(kernelY)
    #print(kernel)
    step1 = convolve(image_2d, kernelX)
    step2 = convolve(step1, kernelY)
    image_new = step2/256

def create_gradients():
    global image_newX
    global image_newY
    global image_out
    image_newX = convolve(image_new, sobel_filterX)
    image_newY = convolve(image_new, sobel_filterY)

    image_out = np.sqrt(np.power(image_newX,2)+np.power(image_newY, 2))


def create_angles():
    global image_angle
    image_angle = np.rad2deg(np.arctan2(image_newY, image_newX))

def hysteresis():
    global image_out
    for i in range(len(image_out)):
        for j in range(len(image_out[0])):
            if image_out[i,j] > max:
                image_out[i,j] = 255
            elif image_out[i,j] < min:
                image_out[i,j] = 0

    for i in range(1,len(image_out)-1):
        for j in range(1,len(image_out[0])-1):
                if image_out[i,j] > max:
                    pass
                elif image_out[i,j] < min:
                    pass
                elif image_out[i,j + 1] > max or image_out[i,j -1] > max or image_out[i + 1,j] > max or image_out[i - 1,j] > max:
                    image_out[i,j] = 255
                elif image_out[i + 1,j + 1] > max or image_out[i + 1,j -1] > max or image_out[i - 1,j + 1] > max or image_out[i - 1,j - 1] > max:
                    image_out[i,j] = 255
                elif image_out[i,j] < max:
                    image_out[i,j] = 0
def non_max_suppression():
    #image_angles_abs = np.abs(image_angles)
    #global image_out_final
    global image_out
    #image_out_final = np.copy(image_out)
    for i in range(1,len(image_out)-1):
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
