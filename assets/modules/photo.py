#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2, os, time

class Photo:
    def __init__(self, path):
        self.count = 0
        self.path = path

    def takePhoto(self):
        image = cv2.imread(os.getcwd() + "/img.jpg")
        #image = cv2.resize(image,(800,600))
        cv2.imwrite(self.path + "/DCIM/img" + str(self.count) + ".jpg",image)
        time.sleep(1)
        os.system ('mpg123 ' + os.getcwd() + '/camera_shutter.mp3')
        self.count = self.count + 1
        return "Taking photo"


#if __name__ == '__main__':
