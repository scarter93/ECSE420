import math
from PIL import Image   #PIL image library for hough -- easier than PNG lib
import time
import threading as thread
#create necessary primitives
num_threads = 4
threads = [None] * num_threads
mutex = thread.Lock()
barrier = thread.Barrier(num_threads)
#create necessary global memory
original = None
new_image = []
new_hough = None
rho_max = 0
d_rho = 0
d_theta = 0

def hough(start_rows, stop_rows, cols, theta_x, rho_y):
    "this function performs actual hough transform for range of rows"
    global new_hough
    global new_image
    #perform hough transform
    for row in range(start_rows, stop_rows):
        for col in range(cols):
            check = original[row, col]
            #check to see if there is actually a line (this may be changed 0 depending on image)
            if check == 0:
                continue
            #if line perform voting
            for entry in range(theta_x):
                theta = d_theta * entry
                rho = row*math.cos(theta) + col*math.sin(theta)
                col_real = rho_y/2 + int(rho/d_rho+0.5)
                #protect memory access when writing "reader/writer" issue
                mutex.acquire()
                new_image[entry, col_real] += 1
                mutex.release()

def setup(image, theta_x, rho_y):
    "setup image for processing"
    global original
    global new_image
    global new_hough
    global rho_max, d_rho, d_theta

    original = image.load()         #load image
    rows, cols = image.size         #get rows and cols from image
    rho_y = int(rho_y/2)*2          #Make sure that this is even

    #create necessary conversion variables
    rho_max = math.hypot(rows, cols)
    if int(rho_max) > rho_y:
        print("rho_y invalid ....exiting....")
        exit(1)

    d_rho = rho_max / (rho_y/2)
    d_theta = math.pi / theta_x

    #create new image for output
    new_hough = Image.new("L", (theta_x, rho_y), 0)
    new_image = new_hough.load()
    return rows, cols
 
def start_threads(rows, cols, theta_x, rho_y):
    "function creates threads and allocates necessary section of image"
    piece = math.ceil(rows/num_threads)
    for i in range(num_threads):
        start = i*piece
        stop = int(min((i+1)*piece, rows))
        threads[i] = thread.Thread(target=hough, args=(start,stop,cols,theta_x,rho_y))
        threads[i].daemon = True
        threads[i].start()

def end_threads():
    "function joins threads after completion"
    for i in range(num_threads):
        threads[i].join()

def min(X,Y):
    "calculates the minimum"
    return X if X < Y else Y
 
def main():
    "runs actual hough transform"
    #variables for transfrom TODO: let user etter values or find min rho_y based on image
    theta_x = 360
    rho_y = 725
    #open image and perform transform
    image = Image.open("out_edge_sup_par.png").convert("L")
    rows, cols = setup(image, theta_x, rho_y)
    start_threads(rows, cols,theta_x, rho_y)
    end_threads()
    #write image
    new_hough.save("ho5_par.png")
 
if __name__ == "__main__":
    "for main"
    file = open('hough_time.csv', 'a')
    start_time = time.time()
    main()
    print(str(time.time() - start_time), file=file)