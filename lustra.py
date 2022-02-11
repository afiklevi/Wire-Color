# AFIK LEVI
# ELIAD PEREZ
# DETECTION OF WIRES COLORS
# PHOTO INPUT

import os
import shutil
import time
from pygame import mixer
import numpy as np
import cv2
from picamera import PiCamera
from time import sleep
from PIL import Image


def min_colored_pixels():
    return 1000


def left_and_right_seperator(img):
    y = 250
    x = 100
    h = 50
    w = 400

    right = img[x:x+w, y:y+h]

    y2 = 665
    x2 = 100
    h2 = 50
    w2 = 400

    left = img[x2:x2+w2, y2:y2+h2]

    left_rot = cv2.rotate(left, cv2.cv2.ROTATE_90_CLOCKWISE)
    right_rot = cv2.rotate(right, cv2.cv2.ROTATE_90_CLOCKWISE)

    return left_rot, right_rot


def threshold_and_contours(left, right):
    gray_left = cv2.cvtColor(left, cv2.COLOR_BGR2GRAY)
    gray_right = cv2.cvtColor(right, cv2.COLOR_BGR2GRAY)

    ## (2) Threshold
    th_left, threshed_left = cv2.threshold(gray_left, 243, 255, cv2.THRESH_BINARY_INV)
    th_right, threshed_right = cv2.threshold(gray_right, 243, 255, cv2.THRESH_BINARY_INV)

    #cv2.imshow("threshed_left", threshed_left)
    #cv2.waitKey()
    #cv2.imshow("threshed_right", threshed_right)
    #cv2.waitKey()

    cnts_left = cv2.findContours(threshed_left, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]
    cnts_right = cv2.findContours(threshed_right, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]
    if (cnts_left == [] or cnts_right == []):
        mixer.music.load("/home/pi/Downloads/error_single.mp3")
        mixer.music.play()
        while mixer.music.get_busy():  # wait for music to finish playing
            time.sleep(1)
        return -1, -1
    ## sorting the object from right to left
    i = 0
    boundingBoxes_left = [cv2.boundingRect(c) for c in cnts_left]
    (cnts_left, boundingBoxes_left) = zip(*sorted(zip(cnts_left, boundingBoxes_left),
                                                  key=lambda b: b[1][i], reverse=True))

    i = 0
    boundingBoxes_right = [cv2.boundingRect(c) for c in cnts_right]
    (cnts_right, boundingBoxes_right) = zip(*sorted(zip(cnts_right, boundingBoxes_right),
                                                    key=lambda b: b[1][i], reverse=True))

    return cnts_left, cnts_right


def pic_maker_of_each_wire(cnts, side, pic):
    k = 0
    for cnt in cnts:
        x, y, w, h = cv2.boundingRect(cnt)
        if cv2.contourArea(cnt) > 500:
            mask = np.zeros(pic.shape[:2], np.uint8)
            cv2.drawContours(mask, [cnt], -1, 255, -1)
            dst = cv2.bitwise_and(pic, pic, mask=mask)

            # changing all black pixels to white
            #height, width, _ = dst.shape
            #for x in range(height):
            #    for j in range(width):
            #        # img[i,j] is the RGB pixel at position (i, j)
            #        # check if it's [0, 0, 0] and replace with [255, 255, 255] if so
            #        if dst[x, j].sum() == 0:
            #            dst[x, j] = [255, 255, 255]

            cv2.imwrite(f"/home/pi/Downloads/Lust/left_and_right/{side}/dst{k}.png", dst)
            #cv2.imshow(f"/home/pi/Downloads/Lust/left_and_right/{side}/dst{k}.png", dst)
            #cv2.waitKey()
            k += 1


def single_color_detector(color, hist, i, color_range_lower, color_range_higher, result):
    tile = cv2.cvtColor(result, cv2.COLOR_BGR2HSV)

    color_mask = cv2.inRange(tile, color_range_lower, color_range_higher)
    color_result = cv2.bitwise_and(result, result, mask=color_mask)

    if np.count_nonzero(color_result) > min_colored_pixels():
        hist[i] = color


    # TODO : showing the mask , need to be deleted at final version
    #cv2.destroyAllWindows()
    #cv2.imshow(f'{color} mask', color_mask)
    #cv2.waitKey()
    #cv2.imshow(f'{color} mask', color_result)
    #cv2.waitKey()


def color_detector_and_counter(side):
    hist = ["", "", ""]
    i = 0
    path = r'/home/pi/Downloads/Lust/left_and_right/'
    path += side + "/"
    path += f"dst{i}.png"
    

    
    result = cv2.imread(path)
    #cv2.imshow("result", result)
    #cv2.waitKey()
    
    while result is not None:
        # Checking for BROWN wires
        brown_lower = np.array([0, 4, 115])
        brown_upper = np.array([180, 55, 240])
        if (hist[i] == ""):
            single_color_detector("brown", hist, i, brown_lower, brown_upper, result)

        deep_brown_lower = np.array([105, 54, 185])
        deep_brown_upper = np.array([180, 113, 232])
        if (hist[i] == ""):
            single_color_detector("brown", hist, i, deep_brown_lower, deep_brown_upper, result)

        # Checking for GREEN+YELLOW wires
        green_lower = np.array([44, 25, 25])
        green_upper = np.array([85, 255, 255])
        if (hist[i] == ""):
            single_color_detector("yellow", hist, i, green_lower, green_upper, result)

        yellow_lower = np.array([20, 100, 100])
        yellow_upper = np.array([30, 255, 255])
        if (hist[i] == ""):
            single_color_detector("yellow", hist, i, yellow_lower, yellow_upper, result)

        # Checking for BLUE wires
        blue_lower = np.array([90, 110, 0])
        blue_upper = np.array([120, 200, 255])
        if (hist[i] == ""):
            single_color_detector("blue", hist, i, blue_lower, blue_upper, result)

        i = i + 1

        path = r'/home/pi/Downloads/Lust/left_and_right/'
        path += side + "/"
        path += f"dst{i}.png"

        result = cv2.imread(path)

    return hist


def hist_matcher(hist_left, hist_right):

    for h in range(3):
        if hist_left[h] == "" or hist_right[h] == "":
            return False
        if hist_right[h] != hist_left[h]:
            return False

    return True


# Starting point
def main():

    camera = PiCamera()
    camera.brightness = 90
    camera.saturation = 0
    camera.contrast = 100

    camera.resolution = (1000, 1000)
    camera.framerate = 15
    #for i in range(100):
    #    camera.contrast = i
        #sleep(0.1)camera.start_preview()
    #camera.start_preview()
    #sleep(3)
    camera.capture('/tmp/lustra.jpg')
    #camera.stop_preview()
    img = cv2.imread("/tmp/lustra.jpg")

    right, left = left_and_right_seperator(img)

    #cv2.imshow("left", left)
    #cv2.waitKey()
    #cv2.imshow("right", right)
    #cv2.waitKey()
    cnts_left, cnts_right = threshold_and_contours(left, right)

    if cnts_right != -1 and cnts_left != -1:

        os.mkdir("/home/pi/Downloads/Lust/left_and_right")
        os.mkdir("/home/pi/Downloads/Lust/left_and_right/left")
        os.mkdir("/home/pi/Downloads/Lust/left_and_right/right")

        pic_maker_of_each_wire(cnts_left, "left", left)
        pic_maker_of_each_wire(cnts_right, "right", right)

        his_1 = color_detector_and_counter("right")
        his_2 = color_detector_and_counter("left")

        mixer.init()

        if hist_matcher(his_2, his_1):
            mixer.music.load("/home/pi/Downloads/Correct.mp3")
            mixer.music.play()
            while mixer.music.get_busy():  # wait for music to finish playing
                time.sleep(1)
        else:
            mixer.music.load("/home/pi/Downloads/Wrong.mp3")
            mixer.music.play()
            while mixer.music.get_busy():  # wait for music to finish playing
                time.sleep(1)
        
        shutil.rmtree("/home/pi/Downloads/Lust/left_and_right/")

    camera.close() 

    #cv2.waitKey()
