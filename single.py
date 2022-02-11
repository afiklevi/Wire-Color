# AFIK LEVI
# ELIAD PEREZ
# DETECTION OF WIRES COLORS
# PHOTO INPUT

import os
import numpy as np
import cv2
import shutil
import time
from pygame import mixer
from picamera import PiCamera
from time import sleep
import numpy as np
import cv2
from picamera import PiCamera
from time import sleep
from PIL import Image

def min_colored_pixels():
    return 1000


def crop_and_rotate(img):

    y2 = 100
    x2 = 50
    h2 = 70
    w2 = 900

    crop = img[x2:x2 + w2, y2:y2 + h2]

    crop_rot = cv2.rotate(crop, cv2.cv2.ROTATE_90_CLOCKWISE)
    #cv2.imshow("threshed", crop_rot)
    #cv2.waitKey()
    return crop_rot


def threshold_and_contours(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ## (2) Threshold
    th, threshed = cv2.threshold(gray, 243, 255, cv2.THRESH_BINARY_INV)

    #cv2.imshow("threshed", threshed)
    #cv2.waitKey()

    cnts = cv2.findContours(threshed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]

    return cnts


def pic_maker_of_each_wire(cnts, pic):
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
                    # img[i,j] is the RGB pixel at position (i, j)
                    # check if it's [0, 0, 0] and replace with [255, 255, 255] if so
            #        if dst[x, j].sum() == 0:
            #            dst[x, j] = [255, 255, 255]

            cv2.imwrite(f"/home/pi/Downloads/dst{k}.png", dst)
            #cv2.imshow(f"dst{k}.png", dst)
            #cv2.waitKey()



def single_color_detector(color, color_range_lower, color_range_higher, result):
    tile = cv2.cvtColor(result, cv2.COLOR_BGR2HSV)

    color_mask = cv2.inRange(tile, color_range_lower, color_range_higher)
    color_result = cv2.bitwise_and(result, result, mask=color_mask)

    if np.count_nonzero(color_result) > min_colored_pixels():
        voice_output(color)
        # TODO : showing the mask , need to be deleted at final version
        # cv2.destroyAllWindows()
        #cv2.imshow(f'{color} mask', color_mask)
        #cv2.waitKey()
        #cv2.imshow(f'{color} mask', color_result)
        #cv2.waitKey()
        return True

    return False


def color_detector():
    i = 0
    path = r'/home/pi/Downloads/'
    path += f"dst{i}.png"

    result = cv2.imread(path)
    
    mixer.init()

    if result is None:
        mixer.music.load("/home/pi/Downloads/error_single.mp3")
        mixer.music.play()
        while mixer.music.get_busy():  # wait for music to finish playing
            time.sleep(1)
        return -1

    done = False
    # Checking for GREEN+YELLOW wires
    if not done:
        green_lower = np.array([44, 25, 25])
        green_upper = np.array([85, 255, 255])
        done = single_color_detector("yellow", green_lower, green_upper, result)

    if not done:
        yellow_lower = np.array([20, 100, 100])
        yellow_upper = np.array([30, 255, 255])
        done = single_color_detector("yellow", yellow_lower, yellow_upper, result)

    # Checking for BLUE wires
    if not done:
        blue_lower = np.array([89, 147, 234])
        blue_upper = np.array([96, 215, 255])
        done = single_color_detector("blue", blue_lower, blue_upper, result)
    # Checking for BROWN wires
    if not done:
        brown_lower = np.array([0, 21, 206])
        brown_upper = np.array([84, 75, 255])
        done = single_color_detector("brown", brown_lower, brown_upper, result)

    if not done:
        deep_brown_lower = np.array([105, 54, 185])
        deep_brown_upper = np.array([180, 113, 232])
        done = single_color_detector("brown", deep_brown_lower, deep_brown_upper, result)
    
    if not done:
        mixer.music.load("/home/pi/Downloads/error_single.mp3")
        mixer.music.play()
        while mixer.music.get_busy():  # wait for music to finish playing
            time.sleep(1)
        return -1

def voice_output (color):
    mixer.init()
    if color is "yellow":
        mixer.music.load("/home/pi/Downloads/yellow-green.mp3")
        mixer.music.play()
        while mixer.music.get_busy():  # wait for music to finish playing
            time.sleep(1)
    elif color is "brown":
        mixer.music.load("/home/pi/Downloads/brown.mp3")
        mixer.music.play()
        while mixer.music.get_busy():  # wait for music to finish playing
            time.sleep(1)
    elif color is "blue":
        mixer.music.load("/home/pi/Downloads/blue.mp3")
        mixer.music.play()
        while mixer.music.get_busy():  # wait for music to finish playing
            time.sleep(1)


# Starting point

# TODO:: add the raspi camera code section
def main():
    camera = PiCamera()
    camera.brightness = 85
    camera.saturation = 0
    camera.contrast = 100

    camera.resolution = (1000, 1000)
    camera.framerate = 15
    #for i in range(100):
    #    camera.contrast = i
        #sleep(0.1)camera.start_preview()
    #camera.start_preview()
    camera.capture('/home/pi/Downloads/Capture/single.jpg')
    #camera.stop_preview()

    img = cv2.imread("/home/pi/Downloads/Capture/single.jpg")


    #cv2.imshow("img", img)
    #cv2.waitKey()
    crop = crop_and_rotate(img)
    cnts = threshold_and_contours(crop)

    pic_maker_of_each_wire(cnts, crop)

    
    if color_detector() != -1:
        os.remove("/home/pi/Downloads/dst0.png")

    camera.close() 
#    cv2.waitKey()