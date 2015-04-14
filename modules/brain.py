#!/usr/bin/python
from datetime import datetime, date, time, timedelta
from dateutil.parser import parse
import os
import re
import sys
import wolframalpha

import stt, tts, calendarAPI, alarm

class Brain:
    def __init__(self):
        self.alarm = alarm.Alarm()
        self.textToSpeech = tts.TTSEngine()
        self.speechToText = stt.STTEngine()
        self.apiSTTkey = 'AIzaSyCFAEJ8_7dR_9IfeJsTEEfbXQ5hZ0v8CxI'
        self.audioName = 'voice.flac'
        self.wolframID = '4X2W9X-AGA34L6QWQ'

        # Your OAuth 2.0 Client ID and Secret. If you do not have an ID and Secret yet,
        # please go to https://console.developers.google.com and create a set.
        self.CLIENT_ID = '71057278230-krkhag877g29lng5rp63qg9bhvoellcn.apps.googleusercontent.com'
        self.CLIENT_SECRET = 'CCaXElmLd89gBUA202L9717t'
        self.APIkey = 'AIzaSyBg0V344J5CuQP_lsfQcIAx0ajv6BOBTfw'
        self.calendarId='0igpmusm3sju2hpmi8a5a382rg@group.calendar.google.com'

    
    def timerBrain(self, text):
        #Ex -> Set timer of 10 minutes
        if self.alarm.setTimer(text):
            print "Timer successfully added"
            self.textToSpeech.say("Timer successfully added")
        else:
            print "invalid input"  
            self.textToSpeech.say("invalid input")  


    def alarmBrain(self, text):
        #Ex->
            #set alarm at 20:00
            #delete alarm
            #get alarm

        dat = re.findall("(\D+)\salarm.+", text)

        if "set" in dat:
            if self.alarm.setAlarm(text):
                print "Alarm successfully added"
                self.textToSpeech.say("Alarm successfully added")
            else:
                print "invalid input"  
                self.textToSpeech.say("invalid input")  

        elif "delete" in dat:
            if self.alarm.deleteAlarm():
                print "Alarm successfully deleted"
                self.textToSpeech.say("Alarm successfully deleted")
            else:
                print "invalid input"  
                self.textToSpeech.say("invalid input") 

        else:
            al = self.alarm.getAlarm
            if al:
                print al
                self.textToSpeech.say(al)
            else:
                print "Not alarm set"  
                self.textToSpeech.say("Not alarm set") 

    def timeBrain(self, text):
        d = datetime.today()

        if "time" in text:
            t = d.strftime("It's %I:%M%p")
        else:
            t = d.strftime("%A %d of %B")
        self.textToSpeech.say(t)
        print t


    def calendarBrain(self, text):
        #'' static words
        #"" input words
        #general questions
            #the 'plans' or 'sheduler' of this 'week' or this 'month'
            #Acces to the 'calendar'
                #Assistant: Accesing to calendar, what do you want to do?
                    #Add:
                        #'Add' new event 'called' "asdfgh" 'for' "this tuesday" (not necessary) 'at' "15:00" of "2 hours"
                        #'Add' new event 'called' "asdsfdg" 'for' "the 7 of march" (not necessary) 'at' "19:00" to "20:00"
                    #List or tell me or get
                        #'List all' my events
                        #'List' the events of this 'week'
                        #'List' the events of this 'month'
                        #'List' the events of "2" 'days'
                        #Get all the elements
                        #Get elements of friday
                    #Delete: -> Ask to confirm the delete
                        #'Delete all' my events 
                        #'Delete all' the events of this 'week'
                        #'Delete all' the events of this 'month'
                        #'Delete the event' of "7 of March" at "15:00"


        calendar = calendarAPI.CalendarAPI(self.CLIENT_ID,self.CLIENT_SECRET,self.APIkey,self.calendarId)
                
        self.textToSpeech.say("What operation do you want to do?")
        os.system("sox -r 16000 -d voice.flac silence 1 0.1 5% 1 1.0 5%")

        text = self.speechToText.voiceRecognitionAndSearch(self.apiSTTkey,self.audioName).lower()
        print text + "\n"
        
        if "add" in text:
            if calendar.setEvents(text):
                text = text.replace('for', 'of')
                text = re.findall("of\s.+",text)[0]
                print text
                #Get event to check if is saved
                events = calendar.getEvents(text)
                for event in events['items']:
                    if event:
                        dt = parse(event['start']['dateTime'])
                        dtf = parse(event['end']['dateTime'])
                        textEvent = "Event called: "+event['summary']+" at "+dt.strftime('%A')+", "+str(dt.day)+" of "+dt.strftime('%B')+" at "+dt.strftime('%H')+":"+dt.strftime('%M')+" to "+dtf.strftime('%H')+":"+dtf.strftime('%M')
                        print textEvent
                        self.textToSpeech.say(textEvent)

                        self.textToSpeech.say("successfully added")
                        print "successfully added"
                    else:
                        self.textToSpeech.say("Not added")
                        print "Not added"
            else:
                self.textToSpeech.say("Incorrect input")
                print "Incorrect input"

        elif "delete" in text:
            if calendar.deleteEvents(text):
                self.textToSpeech.say("successfully deteled")
                print "successfully deteled"

            else:
                self.textToSpeech.say("Nothing to deteled")
                print "Nothing to deteled"

        else:
            events = calendar.getEvents(text)
            for event in events['items']:
                dt = parse(event['start']['dateTime'])
                dtf = parse(event['end']['dateTime'])
                textEvent = "Event called: "+event['summary']+" at "+dt.strftime('%A')+", "+str(dt.day)+" of "+dt.strftime('%B')+" at "+dt.strftime('%H')+":"+dt.strftime('%M')+" to "+dtf.strftime('%H')+":"+dtf.strftime('%M')
                print textEvent
                self.textToSpeech.say(textEvent)
                


    def wolframBrain(self, text):

        client = wolframalpha.Client(self.wolframID)

        res = client.query(text)

        if len(res.pods) > 0:
            texts = ""
            pod = res.pods[1]
            self.textToSpeech.say(pod.text)   
        
        else:
            self.textToSpeech.say("I don't know what do you want")
            print "I don't know what do you want"



    def think(self, text):
        if "timer" in text:
            self.timerBrain(text)

        elif "alarm" in text:
            self.alarmBrain(text)
             
        elif ("time" in text) | ("day" in text) | ("date" in text):
            self.timeBrain(text)

        elif "calendar" in text:
            self.calendarBrain(text)
        else:
            self.wolframBrain(text)
            
        


"""
if __name__ == '__main__':
    text = sys.argv[1:][0]
    brain = Brain()
    brain.think(text)
"""

