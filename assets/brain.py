#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2
import threading
import time
import subprocess
import os 
import signal

from datetime import datetime

from modules import tracker, calendar, alarm, wolfram, music

class Brain:

    def __init__(self):

	self.tracker = tracker.Tracker()
        self.alarm = alarm.Alarm()
        self.calendar = calendar.Calendar()
        self.wolfram = wolfram.Wolfram()
	self.music = music.Music()

    def think(self, text):
        if ("timer" in text) | ("alarm" in text):
            response = self.alarm.think(text)

        elif ("time" in text):
            response = datetime.now().strftime("It's %I:%M%p")

        elif ("day" in text) | ("date" in text):
            response = datetime.now().strftime("%A %d of %B")

        elif ("music" in text) | ("play" in text):
            response = self.music.play()
	            
	elif ("take" in text) | ("photo" in text):

	    response = "taking picture"
	    image = cv2.imread("/home/pi/Desktop/im.jpg")
	    image = cv2.resize(image,(800,600))
	    cv2.imwrite("/hoe/pi/Desktop/def.jpg",image)
	    time.sleep(1)
	    os.system ('mpg321 assets/camera_shutter.mp3')
            
	elif ("wake" in text) | ("up" in text):
	    self.tracker.start()
	    response = "I'm waking up sir"	    

	elif ("down" in text) | ("sleep" in text):
	    self.tracker.stop()
	    response = "I'm going to sleep now"

        elif "calendar" in text:
            response = self.calendar.think(text)
        else:
            response = self.wolfram.think(text)

        return response
