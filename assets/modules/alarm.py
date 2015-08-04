    #!/usr/bin/python
from datetime import datetime, date, time, timedelta
import time
import pytz
from dateutil.parser import parse
import signal
import os
import re
import sys



class Alarm:
    def __init__(self):
        self.getAlarm = None
        self.cest = pytz.timezone('Europe/Madrid')
        signal.signal(signal.SIGALRM, self.handler)

    def handler(self, signum, stack):
        print 'Alarm :', datetime.today().strftime("It's %I:%M:%S%p")
        os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % ( 1, 500))
        self.getAlarm = None

    def setTimer(self,text):
        
        #text -> set 'timer' "of 10 minutes"
        if "for" in text:
             text = text.replace('for', 'of')

        text = re.findall("timer\sof\s(\d+\s\D+)",text)
            #10 minutes
        if text:
            text = re.split("\s",text[0])
            tim = 0
            if (text[1] == "minutes") | (text[1] == "minute"):
                tim = int(text[0])*60
            elif text[1] == "seconds":
                tim = int(text[0])
            elif (text[1] == "hour") | (text[1] == "hours"):
                tim = int(text[0])*3600
            else:
                return False

            signal.alarm(tim)

            d = datetime.now(tz=self.cest) # timezone?
            d = d + timedelta(seconds=tim)
            self.getAlarm = d.strftime("Alarm at %H:%M and %S seconds")

            return True 
        else:
            return False

    def setAlarm(self,text):
        #set 'alarm' "at 19:00"

        text = re.findall("alarm\sat\s(\d+:\d+)",text)

        if text:
            text = re.split(":",text[0])

            hourAlarm = int(text[0])
            minAlarm = int(text[1])
            d = datetime.today()

            tim = (minAlarm*60+hourAlarm*3600)-(int(d.strftime("%M"))*60+int(d.strftime("%H"))*3600+int(d.strftime("%S")))
            
            #Alarm for the next day
            if tim < 0:
                tim = 24*3600 + tim

            signal.alarm(tim)

            d = datetime.now(tz=self.cest) # timezone?
            d = d + timedelta(seconds=tim)
            self.getAlarm = d.strftime("Alarm at %H:%M and %S seconds")

            return True

        else:
            return False

    def deleteAlarm(self):
        #'delete alarm'
        if self.getAlarm:
            signal.alarm(0)
            self.getAlarm = None
            return True
        else:
            return False

    def think(self, text):
        if "timer" in text:
            #Ex -> Set timer of 10 minutes
            if self.setTimer(text):
                return "Timer successfully added"
            else:
                return "invalid input" 

        elif "alarm" in text:
            #Ex->
            #set alarm at 20:00
            #delete alarm
            #get alarm

            dat = re.findall("(\D+)\salarm.+", text)
            if "set" in dat:
                if self.setAlarm(text):
                    return "Alarm successfully added"
                else:
                    return "invalid input"  

            elif "delete" in dat:
                if self.deleteAlarm():
                    return "Alarm successfully deleted"
                else:
                    return "invalid input"

            else:
                al = self.getAlarm
                if al:
                    return al
                else:
                    return "Not alarm set"

