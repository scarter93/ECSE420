import math
from PIL import Image
import time
import threading as thread
 
num_threads = 4
threads = [None] * num_threads
mutex = thread.Lock()
barrier = thread.Barrier(4)

original = None
new_image = []
new_hough = None
rho_max = 0
d_rho = 0
d_theta = 0

def hough(start_rows, stop_rows, cols, theta_x=460, rho_y=360):
    global new_hough
    global new_image
    #perform hough transform
    for row in range(start_rows, stop_rows):
        for col in range(cols):
            check = original[row, col]
            #check to see if there is actually a line (this may be changed 0 depending on image)
            if check == 255:
                continue

            for entry in range(theta_x):
                theta = d_theta * entry
                rho = row*math.cos(theta) + col*math.sin(theta)
                col_real = rho_y/2 + int(rho/d_rho+0.5)
                mutex.acquire()
                new_image[entry, col_real] += 1
                mutex.release()


def setup(image, theta_x=460, rho_y=360):
    global original
    global new_image
    global new_hough
    global rho_max, d_rho, d_theta
    original = image.load()              #load image
    rows, cols = image.size         #get rows and cols from image
    rho_y = int(rho_y/2)*2          #Make sure that this is even

    #create necessary conversion variables
    rho_max = math.hypot(rows, cols)
    d_rho = rho_max / (rho_y/2)
    d_theta = math.pi / theta_x


    #create new image for output
    new_hough = Image.new("L", (theta_x, rho_y), 0)
    new_image = new_hough.load()

    return rows, cols
 

def start_threads(rows, cols):
    piece = math.ceil(rows/num_threads)
    for i in range(num_threads):
        start = i*piece
        stop = int(min((i+1)*piece, rows))
        threads[i] = thread.Thread(target=hough, args=(start,stop,cols))
        threads[i].daemon = True
        threads[i].start()

def end_threads():
    for i in range(num_threads):
        threads[i].join()
 
def main():
    image = Image.open("Pentagon.png").convert("L")
    rows, cols = setup(image)
    start_threads(rows, cols)
    end_threads()
    new_hough.save("ho5_par.png")
 
 
if __name__ == "__main__": 
    start_time = time.time()
    main()
    print("execution time: " + str(time.time() - start_time))