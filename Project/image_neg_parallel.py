import png
import threading as thread
import math
import time
#create necessary global memory
num_threads = 4
threads = [None] * num_threads
new_image = []
image = []

def main():
    "function runs algorothim"
    global image, new_image
    #read image and format
    reader = png.Reader('test.png')
    image_info = reader.read()
    image = list(image_info[2])
    meta = image_info[3]

    if meta['alpha'] == False:
        print("please use an image that has an alpha pixel")
        exit(1)

    new_image = image
    #start execution and join on completion
    start_threads(image)
    end_threads()
    #write image to file
    file_out = open('out_par.png', 'wb')
    out = png.Writer(image_info[0], image_info[1], **image_info[3])
    out.write(file_out, new_image)
    file_out.close()

def worker(start, stop):
    "function performs work for image negation"
    global new_image
    for row in range(start,stop):
        pixel = 0
        #preform image negation on colored image with alpha pixel
        for i in range(int(len(image[0])/4)):
            new_image[row][pixel] = 255 - image[row][pixel]
            new_image[row][pixel+1] = 255 - image[row][pixel+1]
            new_image[row][pixel+2] = 255 - image[row][pixel+2]
            pixel += 4

def start_threads(image):
    "function creates threads and allocates them section of image"
    piece = math.ceil((len(image)/4))
    for i in range(num_threads):
        start = int(i*piece)
        stop = int(min((i+1)*piece, len(image)))
        threads[i] = thread.Thread(target=worker, args=(start, stop))
        threads[i].daemon = True
        threads[i].start()

def end_threads():
    "join threads on completion"
    for i in range(num_threads):
        threads[i].join()

def min(X,Y):
    "calculates the minimum"
    return X if X < Y else Y

if __name__ == "__main__":
    "used to run main"
    file = open('image_neg_time.csv', 'a')
    start_time = time.time()
    main()
    print(str(time.time() - start_time), file=file)