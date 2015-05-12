import cv2
import sys
import time
import serial
import string
from time import sleep

<<<<<<< HEAD
test=serial.Serial("/dev/ttyAMA0",9600)
test.open()

GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.OUT)
pwmX = GPIO.PWM(18,100)
pwmX.start(0)

=======
arduino=serial.Serial("/dev/ttyAMA0",9600)
arduino.isOpen()

>>>>>>> f0af97d0442702cb56fed62cb96b08222dddde06
cascPath = sys.argv[1]
faceCascade = cv2.CascadeClassifier(cascPath)

video_capture = cv2.VideoCapture(0)

servoPanPosition = '0'
<<<<<<< HEAD

test.write(chr(int(90/10 + 2.5)))	

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()
    frame = cv2.resize(frame,(150,90))
=======
	
while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()
    frame = cv2.resize(frame,(140,105))
>>>>>>> f0af97d0442702cb56fed62cb96b08222dddde06
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=1,
<<<<<<< HEAD
        minSize=(5, 5),
=======
        minSize=(10, 10),
>>>>>>> f0af97d0442702cb56fed62cb96b08222dddde06
        flags=cv2.cv.CV_HAAR_SCALE_IMAGE
    )

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
	midFaceX = x+(w/2)
<<<<<<< HEAD
        midScreenX = 75                 
        if(midFaceX < midScreenX - 20):
        	servoPanPosition = 'a'
		test.write(servoPanPosition)
                print "right\n"
	elif(midFaceX > midScreenX + 20):
                servoPanPosition = 'c'
		test.write(servoPanPosition)
                print "left\n"
	else:
		servoPanPosition = 'b'
		print "middle\n"
		               
		
	
=======
        midScreenX = 70                 
        if(midFaceX < midScreenX - 15):	
		arduino.write('l')
                print "right\n"
	elif(midFaceX > midScreenX + 15):
		arduino.write('r')
                print "left\n"
	else:
		print "middle\n"
		               
		
    cv2.imwrite("/home/pi/Desktop/im.jpg", frame)	
>>>>>>> f0af97d0442702cb56fed62cb96b08222dddde06
	
    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
