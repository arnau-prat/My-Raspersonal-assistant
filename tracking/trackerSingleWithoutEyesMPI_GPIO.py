import cv2
import sys
import numpy as np
import itertools
import threading
from mpi4py import MPI
import serial


class Tracker():
    def __init__(self, faceCasc = 'faces.xml', eyesCasc = 'eyes.xml', debug=False):

        self.debug = debug
        self.debugMPI = False
        self.debugGPIO = True
        self.debugTiming = True
        self.faceCasc = faceCasc
        self.eyesCasc = eyesCasc
        self.clahe = None
        self.average = 0
        self.alpha = 0.2
        self.startOffset = 10
        self.hCounter = 0
        self.maxhCounter = 10
        self.maxDiffStatic = 2
        self.lkCounter = 0
        self.maxlkCounter = 3
        self.activeLKAlgorithm = False

        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.rank

        if self.rank == 0:
            self.arduino=serial.Serial("/dev/ttyAMA0",9600)

    def predictFace(self,face, pt0, pt1):
        if not pt0:
            pt0 = pt1
        dx = []
        dy = []

        for p1, p2 in itertools.izip(pt0, pt1):
            dx.append(p2[0] - p1[0])
            dy.append(p2[1] - p1[1])
        if not dx or not dy:
            return face
        midx = round(sum(dx) / len(dx))
        midy = round(sum(dy) / len(dy))

        face = [int(face[0] + midx), int(face[1] + midy), face[2], face[3]]

        # Check total width
        if face[0] <= 0:
            face[0] = 10
        elif (face[0] >= self.maxWidth):
            face[0] = self.maxWidth - 1
        # Check total height
        if face[1] <= 0:
            face[1] = 10
        elif (face[1] + face[3] >= self.maxHeight):
            face[0] = self.maxHeight - face[3] - 1

        return face

    def checkStaticFace(self, faceOld, faceNew):
        static = False
        dx = abs(faceNew[0] - faceOld[0])
        dy = abs(faceNew[1] - faceOld[1])
        diff = (dx + dy) / 2

        if (diff > self.maxDiffStatic):
            self.hCounter = self.hCounter + 1
            if self.hCounter > self.maxhCounter:
                self.hCounter = 0
                self.average = 0
                static = True
        else:
            self.hCounter = 0

        return static



    def checkAberrantFace(self, faceOld, faceNew):
        aberrant = False
        dx = abs(faceNew[0] - faceOld[0])
        dy = abs(faceNew[1] - faceOld[1])
        diff = (dx + dy) / 2

        # Adaptative average
        if self.average == 0:
            self.average = diff

        alg = self.average + diff * self.alpha + self.startOffset

        if (diff > alg):
            aberrant = True
                    
        else:
            self.average = diff


        if self.debug:
            print "***********Check Aberrant Face*********"
            print "Old Face:", faceOld
            print "New Face:", faceNew
            print "average: " + str(self.average)
            print "diff: " + str(diff) + " > " + "alg: " + str(alg) 
            if aberrant:
                print "ABERRANT FACE!!!!!!!!!!"
            print "******************************************"

        return aberrant 

    # Get LK points from last image with face detected
    def getLKPoints(self, img, face):
        # crop image and get face frame
        cropImg = img[face[1]:face[1] + face[3], face[0]:face[0] + face[2]]
        grayFace = cv2.cvtColor(cropImg, cv2.COLOR_BGR2GRAY)
        # Equalize crop image
        grayFace = self.clahe.apply(grayFace)

        if self.debug:
            cv2.imwrite("imgcrop.jpg", cropImg)
            cv2.imwrite("imgcropEquClahe.jpg", grayFace)

            grayFaceEquDebug = cv2.cvtColor(cropImg, cv2.COLOR_BGR2GRAY)
            grayFaceEquDebug = cv2.equalizeHist(grayFaceEquDebug)
            cv2.imwrite("imgcropEquHist.jpg", grayFaceEquDebug)

        # Take face frame and find corners in it with shi-tomasi, get points to follow
        mask = np.zeros_like(grayFace)
        mask[:] = 255
        pt = cv2.goodFeaturesToTrack(grayFace,  mask = mask, **self.feature_params)
        if isinstance(pt, type(None)):
            return pt

        # pt is from a cropped face image. Add x, y in each point.
        for i in xrange(len(pt)):
            pt[i][0][0] = pt[i][0][0] + face[0]
            pt[i][0][1] = pt[i][0][1] + face[1]

        return np.float32(pt).reshape(-1, 1, 2)
    

    def lkCheck(self, p0, p0r, p1):
        # Check Forward-Backward error
        diff = abs(p0 - p0r).reshape(-1, 2).max(-1)
        good = diff < 1
                        
        # Check Aberrant point error
        diff = abs(p1 - p0).reshape(-1, 2).max(-1)
        god = diff < 20
        # Update good points
        good = [go & g for go, g in itertools.izip(good, god)]

        # Check static points
        diff = abs(p1 - p0).reshape(-1, 2).max(-1)
        god = diff > 2

        if (np.sum(god) != len(god)):
            self.lkCounter = self.lkCounter + 1
            if self.lkCounter > self.maxlkCounter:
                # Set Good point all to False
                good = diff < -1
        else: 
            self.lkCounter = 0

        return good

    def moveServo(self, x, w):
        midFaceX = x + w/2
        midScreenX = self.maxWidth/2
        if(midFaceX < midScreenX - 15):
            self.arduino.write('l')
            if self.debug:
                print "++++++++++++++Position Right+++++++++++"
        elif(midFaceX > midScreenX + 15):
            self.arduino.write('r')
            if self.debug:
                print "++++++++++++++Position Left+++++++++++"
        else:
            if self.debug:
                print "++++++++++++++Position Middle+++++++++++"

    def run(self):

        faceCascade = cv2.CascadeClassifier(self.faceCasc)
        eyesCascade = cv2.CascadeClassifier(self.eyesCasc)

        if self.rank == 0:
            video_capture = cv2.VideoCapture(0)
            # Get image size
            ret, img = video_capture.read()
            self.maxHeight = img.shape[0]
            self.maxWidth = img.shape[1]

        self.lk_params = dict(winSize=(10, 10),
                         maxLevel=10,
                         criteria=(cv2.TERM_CRITERIA_EPS |
                                   cv2.TERM_CRITERIA_COUNT, 10, 0.03))

        self.feature_params = dict(maxCorners=4000,
                              qualityLevel=0.6,
                              minDistance=2,
                              blockSize=2)

        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

        startTime = 0
        end = False
        oldFace = []
        p0 = None

        while True:
            if self.debug or self.debugTiming:
                print "Time per Frame in HaarCascade Whitout Eyes:", ((cv2.getTickCount()-startTime)/cv2.getTickFrequency())
                startTime = cv2.getTickCount()

            if self.activeLKAlgorithm:
                self.activeLKAlgorithm = False
                if len(oldFace) == 0:
                    cv2.imshow("Video", img)
                    k = cv2.waitKey(30)
                    if self.debug:
                        print "******************No face****************"
                    continue

                # Get old image and proceed with Lucas-Kanade Algorithm
                face = oldFace
                oldFace = []

                old_pts = None
                # Some points already detected?
                if isinstance(p0, type(None)):
                    p0 = self.getLKPoints(img, face)

                if isinstance(p0, type(None)):
                    if self.debug:
                        print "*********NO LK Points Detected**********"
                    continue

                self.lkCounter = 0

                while True:
                    if self.debug or self.debugTiming:
                        print "Time per Frame in LK:", ((cv2.getTickCount()-startTime)/cv2.getTickFrequency())
                        startTime = cv2.getTickCount()
                    try:
                        # Get new frame
                        ret, img = video_capture.read()
                        # Equalize 
                        newGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        newGray = self.clahe.apply(newGray)

                        if self.debug:
                            cv2.imshow("VideoEqualized", newGray)

                        # Get tracked point
                        p1, st, err = cv2.calcOpticalFlowPyrLK(oldGray, newGray, p0, None, **self.lk_params)
                        p0r, st, err = cv2.calcOpticalFlowPyrLK(newGray, oldGray, p1, None, **self.lk_params)

                        good = self.lkCheck(p0, p0r, p1)

                        if np.sum(good) == 0:
                            # No more points to track
                            if self.debug:
                                print "******NO LK Points To Track******"
                            break

                        new_pts = []
                        for pts, val in itertools.izip(p1, good):
                            if val:
                                new_pts.append([pts[0][0], pts[0][1]])
                                cv2.circle(img, (pts[0][0], pts[0][1]), 2, thickness=2, color=(255, 255, 0))

                        old_pts = []
                        for pts, val in itertools.izip(p0, good):
                            if val:
                                old_pts.append([pts[0][0], pts[0][1]])

                        if self.debug:
                            print "************************Points To Track***********************"
                            print "---------------------------------Old Points---------------------------------"
                            print p0
                            print "---------------------------------Good Old Points---------------------------------"
                            print old_pts
                            print "---------------------------------New Points---------------------------------" 
                            print p1
                            print "---------------------------------Good New Points---------------------------------"
                            print new_pts
                            print "****************************************************************"

                        face = self.predictFace(face, old_pts, new_pts)

                        if self.debug:
                            print "*****************************Face***************************"
                            print face
                            print "****************************************************************"

                        oldGray = newGray
                        p0 = p1

                        # Draw face
                        cv2.rectangle(img, (face[0], face[1]), (face[0] + face[2], face[1] + face[3]), thickness=2, color=(0, 255, 0))
                        cv2.imshow("Video", img)
                        self.moveServo(face[0], face[2])
                        k = cv2.waitKey(30)
                        if k == 27:
                            end = True
                            break
                    except KeyboardInterrupt:
                        end = True
                        break
                if end:
                    break
            else:
                if self.rank == 0:
                    # Capture frame-by-frame
                    ret, img = video_capture.read()
                    #frame = cv2.resize(frame,(140,105))
                    cv2.imwrite("img.jpg", img)
                    
                    oldGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    #oldGray = clahe.apply(oldGray)
                    if self.debug:
                        cv2.imshow("VideoEqualized", oldGray)

                    startTimeMPI = cv2.getTickCount()
                    newFace1ToSend = oldGray[:,:(self.maxWidth/2)+100]
                    newFace2ToSend = oldGray[:,(self.maxWidth/2)-100:]
                    self.comm.send(newFace2ToSend, dest=1)
                    cv2.imshow("VideoEqualized", newFace1ToSend)
                    newFace = faceCascade.detectMultiScale(
                        newFace1ToSend,
                        scaleFactor=1.1,
                        minNeighbors=1,
                        minSize=(100, 100),
                        flags=cv2.cv.CV_HAAR_SCALE_IMAGE
                    )
                    newFace2 = self.comm.recv(source=1)
                    if self.debugMPI:
                        print "newFace1ToSend" , newFace1ToSend
                        print "newFace2ToSend" , newFace2ToSend
                        print "newFace1:", newFace
                        print "newFace2:", newFace2

                    if len(newFace2) != 0:
                        newFace2[0][0] = newFace2[0][0]  + (self.maxWidth/2)-100
                        newFace = newFace2

                    endTimeMPI = cv2.getTickCount()
                    if self.debugTiming:
                        print "MPI:",((endTimeMPI - startTimeMPI)/cv2.getTickFrequency())

                if self.rank == 1:
                    oldGray2 = self.comm.recv(source=0)
                    if self.debugMPI:
                        print "data recieved:", oldGray2
                    newFace2 = faceCascade.detectMultiScale(
                        oldGray2,
                        scaleFactor=1.1,
                        minNeighbors=1,
                        minSize=(100, 100),
                        flags=cv2.cv.CV_HAAR_SCALE_IMAGE
                    )
                    self.comm.send(newFace2, dest=0)

                if self.rank == 0:
                    # Using the previous face
                    if (len(oldFace) != 0 and len(newFace) != 0) :
                        if(self.checkStaticFace(oldFace, newFace[0])):
                            # Static Face, Skip this face
                            continue

                        if(self.checkAberrantFace(oldFace, newFace[0])):
                            # Aberrant Face, Skip this face
                            continue

                    if(len(newFace) != 0):           
                        cv2.rectangle(img, (newFace[0][0], newFace[0][1]), (newFace[0][0] + newFace[0][2], newFace[0][1] + newFace[0][3]), thickness=2, color=(0, 255, 0))
                        cv2.imshow("Video", img)
                        self.moveServo(newFace[0][0], newFace[0][2])
                        k = cv2.waitKey(30)
                        # Face detected, continue with HarrCascade
                        oldFace = newFace[0]
                    else:
                        self.activeLKAlgorithm = True
                

        # When everything is done, release the capture
        video_capture.release()
        cv2.destroyAllWindows()
        self.stop = False

if __name__ == '__main__':
    # Traking Test
    tracker = Tracker()
    tracker.run()
    
    
