# AFIK LEVI
# ELIAD PEREZ
# DETECTION OF WIRES COLORS
# PHOTO INPUT

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import os
import shutil
import time
from pygame import mixer
import numpy as np
from picamera import PiCamera
from time import sleep
from PIL import Image
import main_test
import single
import lustra


def short_button_callback():
    mixer.music.load("/home/pi/Downloads/single_mode.mp3")
    mixer.music.play()
    while mixer.music.get_busy():  # wait for music to finish playing
        time.sleep(1)
    single.main()
    
def long_button_callback():
    mixer.music.load("/home/pi/Downloads/lustra_mode.mp3")
    mixer.music.play()
    while mixer.music.get_busy():  # wait for music to finish playing
        time.sleep(1)
    lustra.main()

def welcome():
    mixer.music.load("/home/pi/Downloads/welcome.mp3")
    mixer.music.play()
    while mixer.music.get_busy():  # wait for music to finish playing
        time.sleep(1)


 # Setup event on pin 10 rising edge

mixer.init()

welcome()

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)

while True:
    if GPIO.input(10):
        pressed_time = time.monotonic()
        while GPIO.input(10):
            pass
        pressed_time = time.monotonic() - pressed_time
        if pressed_time <=0.5:
            short_button_callback()
        else:
            long_button_callback()
        
#right button
#GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
#GPIO.add_event_detect(10,GPIO.RISING,callback=right_button_callback, bouncetime=1000)

#left button
#GPIO.setup (12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
#GPIO.add_event_detect(12,GPIO.RISING,callback=left_button_callback, bouncetime=1000)

#busy wait for button
message = input()
    
GPIO.cleanup() # Clean up