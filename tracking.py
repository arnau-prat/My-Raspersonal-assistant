import cv2
import sys
import RPi.GPIO as GPIO
import time

DEBUG = True

GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.OUT)
pwm = GPIO.PWM(18,100)
pwm.start(0)
pwm.ChangeDutyCycle(11)

offSet =0

faceCascade = cv2.CascadeClassifier("faces.xml")

video_capture = cv2.VideoCapture(0)

width = video_capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
height = video_capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)

posMid = width/2

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.cv.CV_HAAR_SCALE_IMAGE
    )

    if DEBUG:

    	# Draw a rectangle around the faces
    	for (x, y, w, h) in faces:
		
        	cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
		print "Position:("+str(x+w/2)+","+str(y+h/2)+")"
		position = 90-60*((x+w/2-width/2)/width)
		print "result: "+ str(position)
		pwm.ChangeDutyCycle(position/10+2.5)
		offSet = offSet + x - posMid
    	# Display the resulting frame
    	cv2.imshow('Video', frame)


    else:
   		
        # Relative position of the faces
   		for (x, y) in faces:
   			print "Position:("+str(x)+","+str(y)+")"


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()

		



		


