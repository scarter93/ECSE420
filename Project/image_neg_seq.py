import png
import time
#import numpy as np
import threading as thread

def main():
    file_out = open('Pentagon_edge.png', 'wb')
    reader = png.Reader('Pentagon.png')
    image_info = reader.read()
    image = list(image_info[2])
    #image = np.vstack(map(np.uint16, image))

    new_image = []
    for row in range(len(image)):
        pixel = 0
        new_image.append(list(image[row]))
        for i in range(image_info[0]):
            new_image[row][pixel] = 255 - image[row][pixel]
            new_image[row][pixel+1] = 255 - image[row][pixel+1]
            new_image[row][pixel+2] = 255 - image[row][pixel+2]
            pixel += 4

    print(new_image)
    out = png.Writer(image_info[0], image_info[1], **image_info[3])
    out.write(file_out, new_image)
    file_out.close()


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("execution time: " + str(time.time() - start_time))

