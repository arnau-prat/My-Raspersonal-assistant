import cv2
import sys
import RPi.GPIO as GPIO
import time

DEBUG = True

GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.OUT)
pwmX = GPIO.PWM(18,100)
pwmX.start(0)
pwmX.ChangeDutyCycle(11)
pwmY = GPIO.PWM(19,100)
pwmY.start(0)
pwmY.ChangeDutyCycle(11)

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

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        if DEBUG:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.imshow('Video', frame)
            print "Pos:(" + str(x + w/2) + "," + str(y + h/2) + ")"
        #new servo position on the x axis
        positionX = 90 - 60 * ((x + w/2 - width/2)/width)
        pwmX.ChangeDutyCycle(positionX/10 + 2.5)
        #new servo position on the x axis
        positionY = 90 - 60 * ((y + h/2 - height/2)/height)
        pwmX.ChangeDutyCycle(positionY/10 + 2.5)
        # Display the resulting frame


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()

		



		


