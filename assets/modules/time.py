#!/usr/bin/python
    
import sys
import os
from oauth2client import client

import gflags
import httplib2

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

from datetime import datetime, date, time, timedelta
import pytz
from dateutil.parser import parse
import re

import tts,stt


class CalendarAPI:
    def __init__(self,client_id = '71057278230-krkhag877g29lng5rp63qg9bhvoellcn.apps.googleusercontent.com'
                    ,client_secret = 'CCaXElmLd89gBUA202L9717t'
                    ,APIkey = 'AIzaSyBg0V344J5CuQP_lsfQcIAx0ajv6BOBTfw'
                    ,calendarId = '0igpmusm3sju2hpmi8a5a382rg@group.calendar.google.com' ):

        # Your OAuth 2.0 Client ID and Secret. If you do not have an ID and Secret yet,
        # please go to https://console.developers.google.com and create a set.

        self.stt = stt.STTEngine()
        self.tts = tts.TTSEngine()

        cest = pytz.timezone('Europe/Madrid')
        self.now = datetime.now(tz=cest) # timezone?
        self.dt = parse(str(self.now))

        self.calendarId = calendarId
        self.weekDay = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']

        # The calendar API OAuth 2.0 scope.
        SCOPE = u'https://www.googleapis.com/auth/calendar'
        #Retrieve and display the access and refresh token.
        flow = client.OAuth2WebServerFlow(
            client_id=client_id,
            client_secret=client_secret,
            scope=[SCOPE],
            user_agent='Ads Python Client Library',
            redirect_uri='urn:ietf:wg:oauth:2.0:oob')
        authorize_url = flow.step1_get_authorize_url()

        storage = Storage('calendar.dat')
        credentials = storage.get()
        if credentials is None or credentials.invalid == True:
            credentials = run(flow, storage)

        # Create an httplib2.Http object to handle our HTTP requests and authorize it
        # with our good Credentials.
        http = httplib2.Http()
        http = credentials.authorize(http)

        # Build a service object for interacting with the API. Visit
        # the Google Developers Console
        # to get a developerKey for your own application.
        service = build(serviceName='calendar', version='v3', http=http, developerKey=APIkey)
        self.service = service

    def getEvents(self, text):
        #'List all' my events
        #'List' the events of this 'week'
        #'List' the events of this 'month'
        #'List' the events of "2" 'days'
        #'List' the event of "7 of March" at "15:00"
        #'List' the event of "this friday"

        if "week" in text:
            days = 7
        elif "month" in text:
            days = 30 - int(self.dt.strftime('%d'))
        elif "days" in text:
            days = int(re.findall("(\d+)",text)[0])
        elif "all" in text:
            days = 0
        else:
            days = -1

            dat = re.findall("of\s(.+)",text)
                #"7 of March" at "15:00"
                #"this friday"
            if dat:
                dat = dat[0]
            else:
                days = 0
            
            #Get only date and not time
            da = re.findall("at\s\d+:\d+", dat)
            if da:
                dat = re.findall("(.+)\sat",dat)[0]
                    #"7 of March"
                    #"this friday"

            #deleteDay = -1 -> Actual day because day not set
            #deleteDay = 1 -> Get all input day 
            #deleteDay = 0 -> Get an interval of time

            #By default get all the day
            deleteDay = 1

            #Check if there are a number or a day of the week
            day = re.findall("[0-9]",dat)


            if day:
                #"7 of March"
                dayEvent = int(day[0])
                monthRe = re.findall("of\s([a-z]+)",dat)
                monthEvent = int(datetime.strptime(monthRe[0], '%B').strftime('%m'))
            else:
                #"this friday"
                #Get the week day
                dat = re.split('\s+', dat)
                day = set(dat).intersection(self.weekDay)


                if day:
                    day = day.pop()
                    #Compare the actual time with the input time
                    posNow = self.weekDay.index( self.dt.strftime('%A').lower())
                    pos = self.weekDay.index(day)
                    if (pos - posNow) < 0:
                        posCount = abs(pos - posNow) + 1
                    else:
                        posCount = pos - posNow

                    dayEvent = int( self.dt.strftime('%d')) + posCount
                    monthEvent = int( self.dt.strftime('%m'))
                else:
                    #No date set, get actual day
                    deleteDay = -1
                    

            
            inter = re.findall("of.+",text)[0]
                #of "7 of March" at "15:00"
                #of "this friday"

            #Check if we have time
            da = re.findall("at\s\d+:\d+", inter)
            if da:
                #time set, time not all day
                deleteDay = 0

                tim = re.findall("at\s(\d+:\d+)",text)[0]
                tim = tim.split(':')
                hourEvent = int(tim[0])
                minEvent = int(tim[1])
                

        if days == -1:            
            #deleteDay = -1 -> Actual day because day not set
            #deleteDay = 1 -> Get all input day 
            #deleteDay = 0 -> Get an interval of time
            if deleteDay == -1:
                timeMin = datetime(year=self.now.year, month=self.now.month, day=self.now.day, hour=0, minute=0)
                timeMax = timeMin + timedelta(minutes=1435) #1435
                timeMin = timeMin.isoformat() + self.dt.strftime('%z')
                timeMax = timeMax.isoformat() + self.dt.strftime('%z')
                
            elif deleteDay == 1:
                timeMin = datetime(year=self.now.year, month=monthEvent, day=dayEvent, hour=0, minute=0)
                timeMax = timeMin + timedelta(minutes=1435) #1435
                timeMin = timeMin.isoformat() + self.dt.strftime('%z')
                timeMax = timeMax.isoformat() + self.dt.strftime('%z')
            else:
                #Get all the events of the day
                timeMin = datetime(year=self.now.year, month=monthEvent, day=dayEvent, hour=0, minute=0)
                timeMax = timeMin + timedelta(minutes=1435) #1435
                timeMin = timeMin.isoformat() + self.dt.strftime('%z')
                timeMax = timeMax.isoformat() + self.dt.strftime('%z')
                events = self.service.events().list(calendarId=self.calendarId,timeMin=timeMin, timeMax=timeMax).execute()

                #Calcule the start time of the event (minutes)
                timeStart = hourEvent*60 + minEvent
                count=0
                evet = events
                #Get every event and check the start time
                for event in events['items']:
                    #'2015-03-08T14:00:00+01:00'
                    dt = parse(event['start']['dateTime'])
                    if (int(dt.strftime('%H'))*60+int(dt.strftime('%M'))) == timeStart:
                        evet['items'][0] = event
                    else:
                        #Count of unmached events
                        count = count +1

                #Remove unmatched events
                for i in range(count):
                    evet['items'].pop()

                return evet


            events = self.service.events().list(calendarId=self.calendarId,timeMin=timeMin, timeMax=timeMax).execute()
            
        #Get all the events
        elif days == 0:
            events = self.service.events().list(calendarId=self.calendarId).execute()

        #Get the events depending of the days interval
        else:
            timeMax = datetime(year=self.now.year, month=self.now.month, day=self.now.day, tzinfo=cest) + timedelta(days=days)
            timeMax = timeMax.isoformat() 

            events = self.service.events().list(calendarId=self.calendarId,timeMax=timeMax).execute()

        return events 



    def setEvents(self, text):

        #'Add' new event called "asdfgh" 'for' "this tuesday" (not necessary) 'at' "15:00" of "2 hours"
        #'Add' new event called "asdsfdg" 'for' "the 7 of march" (not necessary) 'at' "19:00" to "20:00"

        summary = re.findall("called\s([a-z,0-9,\s]+)\sfor",text)
        if summary:
            summary = summary[0]
        else:
            summary = "event"

        dat = re.findall("for\s(.+)",text)[0]
            #"7 of March" at "15:00"
            #"this friday"
        
        #Get only date and not time
        da = re.findall("at\s\d+:\d+", dat)
        if da:
            dat = re.findall("(.+)\sat",dat)[0]
                #"7 of March"
                #"this friday"
        #Check if there are a number or a day of the week
        day = re.findall("[0-9]",dat)
        if day:
            #"7 of March"
            dayEvent = int(day[0])
            monthRe = re.findall("of\s([a-z]+)",dat)
            monthEvent = int(datetime.strptime(monthRe[0], '%B').strftime('%m'))
        else:
            #"this friday"
            #Get the week day
            dat = re.split('\s+', dat)
            day = set(dat).intersection(self.weekDay)

            if day:
                day = day.pop()
                #Compare the actual time with the input time
                posNow = self.weekDay.index( self.dt.strftime('%A').lower())
                pos = self.weekDay.index(day)
                if (pos - posNow) < 0:
                    posCount = abs(pos - posNow) + 1
                else:
                    posCount = pos - posNow

                dayEvent = int( self.dt.strftime('%d')) + posCount
                monthEvent = int( self.dt.strftime('%m'))
            else:
                #Get actual date if day of the week or number day is not set
                dayEvent = int( self.dt.strftime('%d'))
                monthEvent = int( self.dt.strftime('%m'))



        inter = re.findall("for.+",text)[0]
        #Check if we have time
        da = re.findall("at\s\d+:\d+", inter)
        if da:
            tim = re.findall("at\s(\d+:\d+)",text)[0]
            tim = tim.split(':')
            hourEvent = int(tim[0])
            minEvent = int(tim[1])

            #Check if we have interval
            inte = re.findall("at\s\d+:\d+(.+)",text)[0]
            #Check the type of interval
            da = re.findall("of\s\d+\s\D+", dat)
            daa = re.findall("\d+:\d+\sto\s\d+:\d+", dat)
            if da:
                inte = re.split('\s+', inte)
                #Check the scale
                if "minutes" in inte[3]:
                    intervalEvent = int(inte[2])
                elif "hours" in inte[3]:
                    intervalEvent = int(inte[2])*60
                elif "hour" in inte[3]:
                    intervalEvent = int(inte[2])*60 
                else:
                    return False

            elif daa:
                inte = re.split('\s+', inte)    
                interEv = inte[2].split(':')
                intervalEvent = (int(interEv[0])*60 + int(interEv[1]))-(hourEvent*60 + minEvent)
                if intervalEvent < 0:
                    return False
            else:
                #Interval time by default
                intervalEvent = 60
        else:
            #Event by default from 08:00 to 22:00
            hourEvent = 8
            minEvent = 0
            intervalEvent = 14*60

        startTime = datetime(year=self.now.year, month=monthEvent, day=dayEvent, hour=hourEvent, minute=minEvent) 

        endTime = startTime + timedelta(minutes=intervalEvent)
        startTime = startTime.isoformat() + self.dt.strftime('%z')
        endTime = endTime.isoformat() + self.dt.strftime('%z')

        body = {'summary':summary, 'start':{'dateTime': startTime}, 'end':{'dateTime':endTime}}

        event = self.service.events().insert(calendarId=self.calendarId, body=body).execute()

        return True



    def deleteEvents(self, text):
        #'Delete all' my events 
        #'Delete all' the events of this 'week'
        #'Delete all' the events of this 'month'
        #'Delete the event' of "7 of March" at "15:00"

        events = self.getEvents(text)

        for event in events['items']:
            self.service.events().delete(calendarId=self.calendarId, eventId=event['id']).execute()

        #Return True if something was deleted
        if events['items']:
            return True
        else:
            return False


    def thinkCalendar(self, text):

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

                
        self.tts.say("What operation do you want to do?")
        print "What operation do you want to do?" + "\n"

        os.system("sox -d voice1.flac silence 1 0.1 5% 1 1.0 5%")
        text = self.stt.transcript("voice1.flac").lower()
        print text 

        if "add" in text:
            if self.setEvents(text):
                #Convert text of 'add event' to 'get events' 
                text = text.replace('for', 'of')
                #Delete unnecesary text
                text = re.findall("of\s.+",text)[0]
                
                #Get event to check if is saved
                events = self.getEvents(text)
                for event in events['items']:
                    if event:
                        dt = parse(event['start']['dateTime'])
                        dtf = parse(event['end']['dateTime'])
                        textEvent = "Event called: "+event['summary']+" at "+dt.strftime('%A')+", "+str(dt.day)+" of "+dt.strftime('%B')+" at "+dt.strftime('%H')+":"+dt.strftime('%M')+" to "+dtf.strftime('%H')+":"+dtf.strftime('%M')
                        textEvent += ". Successfully added"         
                        return textEvent                
                    else:
                        return "Not added"     
            else:
                return "Incorrect input"

        elif "delete" in text:
            if self.deleteEvents(text):
                return "successfully deteled"

            else:
                return "Nothing to detele"

        else:
            textEvent = ""
            events = self.getEvents(text)
            for event in events['items']:
                dt = parse(event['start']['dateTime'])
                dtf = parse(event['end']['dateTime'])
                textEvent += "Event called: "+event['summary']+" at "+dt.strftime('%A')+", "+str(dt.day)+" of "+dt.strftime('%B')+" at "+dt.strftime('%H')+":"+dt.strftime('%M')+" to "+dtf.strftime('%H')+":"+dtf.strftime('%M') + "\n"
            return textEvent
            
                


"""
if __name__ == '__main__':

    text0 = 'Add new event called prueb1 for this tuesday at 19:00 to 21:00'
    text1 = 'Add new event called my lunch for the 10 of march at 19:00 of 1 hours'
    text2 = 'Add new event called my lunch for the 15 of march'
    text3 = 'Add new event called my lunch for the 12 of april at 20:00 of 30 minutes'
    textGet = 'Delete the events of the 4 of april'
    textGet1 = 'Get all the events'
    textDel =  'Delete the events of this friday'
    #text = 'get the events of this friday'

    returnedText = sys.argv[1:][0]
    print "input text:"
    print text + "\n"

    print returnedText + "\n"
    
    if "add" in returnedText:
        if calendar.setEvents(returnedText):
            returnedText = returnedText.replace('for', 'of')
            returnedText = re.findall("of\s.+",returnedText)[0]
            print returnedText
            events = calendar.getEvents(returnedText)
            for event in events['items']:
                dt = parse(event['start']['dateTime'])
                dtf = parse(event['end']['dateTime'])
                textEvent = "Event called: "+event['summary']+" at "+dt.strftime('%A')+", "+str(dt.day)+" of "+dt.strftime('%B')+" at "+dt.strftime('%H')+":"+dt.strftime('%M')+" to "+dtf.strftime('%H')+":"+dtf.strftime('%M')
                print textEvent
                say(textEvent)

            say("Succesfully added")
            print "Succesfully added"
        else:
            say("Incorrect input")
            print "Incorrect input"
    elif "delete" in returnedText:
        if calendar.deleteEvents(returnedText):
            say("Succesfully deteled")
            print "Succesfully deteled"
        else:
            say("Nothing to deteled")
            print "Nothing to deteled"
    else:
        events = calendar.getEvents(returnedText)
        for event in events['items']:
            dt = parse(event['start']['dateTime'])
            dtf = parse(event['end']['dateTime'])
            textEvent = "Event called: "+event['summary']+" at "+dt.strftime('%A')+", "+str(dt.day)+" of "+dt.strftime('%B')+" at "+dt.strftime('%H')+":"+dt.strftime('%M')+" to "+dtf.strftime('%H')+":"+dtf.strftime('%M')
            print textEvent
            say(textEvent)
"""

