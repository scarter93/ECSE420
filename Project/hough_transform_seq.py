import math
from PIL import Image
#import threading as thread
import time
 
def hough(image, theta_x=460, rho_y=360):
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
 
    
    #perform hough transform
    for row in range(rows):
        for col in range(cols):
            check = original[row, col]
            #check to see if there is actually a line (this may be changed 0 depending on image)
            if check == 0:
                continue

            for entry in range(theta_x):
                theta = d_theta * entry
                rho = row*math.cos(theta) + col*math.sin(theta)
                col_real = rho_y/2 + int(rho/d_rho+0.5)
                new_image[entry, col_real] += 1
    #return result of conversion
    return new_hough
 
 
def main():
    "Test Hough transform with pentagon."
    image = Image.open("out_edge_sup.png").convert("L")
    out = hough(image, 2000, 2000)
    out.save("ho5_pent.png")
 
 
if __name__ == "__main__": 
    start_time = time.time()
    main()
    print("execution time: " + str(time.time() - start_time))