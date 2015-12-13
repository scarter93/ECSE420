import png
import threading as thread
import math
import time

num_threads = 4
threads = [None] * num_threads
new_image = []
image = []

def main():
    global image, new_image
    reader = png.Reader('test.png')
    image_info = reader.read()
    image = list(image_info[2])
    new_image = image

    start_threads(image)
    end_threads()

    file_out = open('out_par.png', 'wb')
    out = png.Writer(image_info[0], image_info[1], **image_info[3])
    out.write(file_out, new_image)
    file_out.close()

def worker(start, stop):
    global new_image
    for row in range(start,stop):
        pixel = 0
        for i in range(int(len(image[0])/4)):
            new_image[row][pixel] = 255 - image[row][pixel]
            new_image[row][pixel+1] = 255 - image[row][pixel+1]
            new_image[row][pixel+2] = 255 - image[row][pixel+2]
            pixel += 4

def start_threads(image):
    piece = math.ceil((len(image)/4))
    for i in range(num_threads):
        start = int(i*piece)
        stop = int(min((i+1)*piece, len(image)))
        threads[i] = thread.Thread(target=worker, args=(start, stop))
        threads[i].daemon = True
        threads[i].start()

def end_threads():
    for i in range(num_threads):
        threads[i].join()

def min(X,Y):
    return X if X < Y else Y

if __name__ == "__main__":
    start_time = time.time()
    main()
    print("execution time: " + str(time.time() - start_time))