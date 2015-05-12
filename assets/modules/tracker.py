import cv2
import sys
import time
import serial
import string
import threading

class Tracker(threading.Thread):

	def __init__(self):
		super(Tracker, self).__init__()
		self.arduino=serial.Serial("/dev/ttyAMA0",9600)
		self.arduino.isOpen()
		self.cascPath = "../../faces.xml"
		self.faceCascade = cv2.CascadeClassifier(self.cascPath)

	def run(self):
		self.video_capture = cv2.VideoCapture(0)
		self.arduino.write('w')
		cv2.destroyAllWindows()

		while True:
    			# Capture frame-by-frame
    			ret, frame = self.video_capture.read()
    			frame = cv2.resize(frame,(140,105))
    
   			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    			faces = self.faceCascade.detectMultiScale(
        			gray,
        			scaleFactor=1.1,
        			minNeighbors=1,
        			minSize=(10, 10),
        			flags=cv2.cv.CV_HAAR_SCALE_IMAGE
    			)

    			# Draw a rectangle around the faces
    			for (x, y, w, h) in faces:
        			cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
				midFaceX = x+(w/2)
        			midScreenX = 70                 
        			if(midFaceX < midScreenX - 15):
					test.write('r')
                			print "right\n"
				elif(midFaceX > midScreenX + 15):
					test.write('l')
                			print "left\n"
				else:
					print "middle\n"
		     
    			cv2.imshow('Video', frame)
			
			

	def stop(self):
		
		self.arduino.write('s')
		self.video_capture.release()
		cv2.destroyAllWindows()
