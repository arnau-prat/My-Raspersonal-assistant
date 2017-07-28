#!/usr/bin/python

import httplib2
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.tools import run
from oauth2client import client

from datetime import datetime, timedelta
import pytz
from dateutil.parser import parse
import re, sys, os

class CalendarAPI:
    def __init__(self, path, isCalendar):
         
        client_id = '###################################'
        client_secret = '######################'
        APIkey = '############################'
        if isCalendar:
            calendarId = '###########################'
        else:
            calendarId = '#############################' 
        
        # Your OAuth 2.0 Client ID and Secret. If you do not have an ID and Secret yet,
        # please go to https://console.developers.google.com and create a set.

        self.cest = pytz.timezone('Europe/Madrid')
        self.now = datetime.now(tz=self.cest) # timezone?
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

        storage = Storage(path + 'calendar.dat')
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
        
    def getWeekDay(self, date):
        date = [date]
        day = set(date).intersection(self.weekDay)
        dayEvent = -1

        if day:
            day = day.pop()
            #Compare the actual time with the input time
            posNow = self.weekDay.index( self.dt.strftime('%A').lower())
            pos = self.weekDay.index(day)
            posCount = pos - posNow
            if posCount < 0:
                posCount = posCount + 7
            else:
                posCount = pos - posNow
                
            dayEvent = int( self.dt.strftime('%d')) + posCount
        return dayEvent

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

        elif any(weekDay in text for weekDay in self.weekDay):
            days = -1
            currentDay = 1
            #Get the week day
            date = re.findall('\s(\w+)$', text)
            if date:
                date = date[0]
                dayEvent = self.getWeekDay(date)
                if dayEvent > 0:
                    monthEvent = int( self.dt.strftime('%m'))
                    currentDay = 0
                
        else:
            days = -1
            currentDay = 1
            day = ""
            month = ""
            parsedText = re.findall("(\d+)\w*\sof\s(\w+)(\sat\s\d+:\d+)?$", text)


            if parsedText:
                parsedText = parsedText[0]
                day = parsedText[0]
                month = parsedText[1]
                if (day != "") & (month != ""):
                    dayEvent = int(day)
                    monthEvent = int(datetime.strptime(month, '%B').strftime('%m'))
                    currentDay = 0
                parsedTime = parsedText[2]
                #Check if we have time
                if parsedTime:
                    #time set, time not all day
                    currentDay = -1
                    
                    tim = re.findall("at\s(\d+:\d+)",parsedTime)[0]
                    tim = tim.split(':')
                    hourEvent = int(tim[0])
                    minEvent = int(tim[1])
            else:
                parsedText = re.findall("(\d+)\w*\sof\s(\w+)\sat\s(\d+)\s(\w\.\w\.)*.*", text)
                if parsedText:
                    parsedText = parsedText[0]
                    day = parsedText[0]
                    month = parsedText[1]
                    if (day != "") & (month != ""):
                        dayEvent = int(day)
                        monthEvent = int(datetime.strptime(month, '%B').strftime('%m'))
                        currentDay = 0
                    parsedTime = parsedText[2]
                    #Check if we have time
                    if parsedTime:
                        #time set, time not all day
                        currentDay = -1

                        hourEvent = int(parsedTime)
                        minEvent = 0
                        pmam =  parsedText[3]
                        if pmam == "p.m.":
                            hourEvent = hourEvent + 12
                            if hourEvent > 23:
                                hourEvent = 0
                else:
                    days = 0

        if days == -1:            
            #currentDay = 1 -> Actual day because day not set
            #currentDay = 0 -> Get all input day 
            #currentDay = -1 -> Get an interval of time (special case for check the add events)
            if currentDay == 1:
                timeMin = datetime(year=self.now.year, month=self.now.month, day=self.now.day, hour=0, minute=0)
                timeMax = timeMin + timedelta(minutes=1435) #1435
                timeMin = timeMin.isoformat() + self.dt.strftime('%z')
                timeMax = timeMax.isoformat() + self.dt.strftime('%z')
                
            elif currentDay == 0:
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
            timeMax = datetime(year=self.now.year, month=self.now.month, day=self.now.day, tzinfo=self.cest) + timedelta(days=days)
            timeMax = timeMax.isoformat() 

            events = self.service.events().list(calendarId=self.calendarId,timeMax=timeMax).execute()

        return events 




    def setEvents(self, text):
        # Before text:
            # Create a calendar event for asdf
            # Create a calendar event called asdf
            # Create a calendar event asdf
        # After text:
            # asdf, Saturday at 7 pm
            # asdf for this Saturday
            # asdf this Saturday
            # asdf for the 5th of April at 15:00 of 2 hours
            # adsf for the 7 of march at 19:00 to 20:00

        if "remind me to" in text:
            parsedText = re.findall("(remind\sme\sto\s)([\w\s]*[^f][^o][^r])\s(for\sthe|for\sthis|the|this)\s([\w\s]*)(\sat.*)?$",text)
        else:
            parsedText = re.findall("\sevent(\sfor|\scalled)?\s([\w\s]*[^f][^o][^r])\s(for\sthe|for\sthis|the|this)\s([\w\s]*)(\sat.*)?$",text)
        if parsedText:
            parsedText = parsedText[0]
            # for | called
            summary = parsedText[1]
            # for the | this | for this
            parseDate = parsedText[3]
            parseTime = parsedText[4]
        else:
            return False
        
        #Check if there are a number or a day of the week
        day = re.findall("\d+",parseDate)
        if day:
            # 5th of April
            # 7 of March
            
            dayEvent = int(day[0])
            monthRe = re.findall("of\s([a-z]+)",parseDate)
            # Check
            if (not dayEvent) | (not monthRe):
                return False
            
            monthEvent = int(datetime.strptime(monthRe[0], '%B').strftime('%m'))
        else:
            # Saturday

            # Get the week day
            dayEvent = self.getWeekDay(parseDate)

            if dayEvent > 0:
                monthEvent = int( self.dt.strftime('%m'))
            else:
                #Get actual date if day of the week or number day is not set
                dayEvent = int( self.dt.strftime('%d'))
                monthEvent = int( self.dt.strftime('%m'))

        # Get time
        if parseTime:
            tim = re.findall("at\s(\d+:\d+).*",parseTime)
            if tim:
                tim = tim[0].split(':')
                hourEvent = int(tim[0])
                minEvent = int(tim[1])
            elif ("p.m." in parseTime) | ("a.m." in parseTime):
                # Get time am|pm
                tim = re.findall("at\s(\d+)\s(\w\.\w\.)*.*", parseTime)
                if tim:
                    tim = tim[0]
                    hourEvent = int(tim[0])
                    pmam = tim[1]
                    if pmam == "p.m.":
                        hourEvent = hourEvent + 12
                        if hourEvent > 23:
                            hourEvent = 0
                minEvent = 0
            else: 
                return False
            
            
            #Interval time by default
            intervalEvent = 60
            #Check if we have interval
            parseInterval = re.findall("(of|to)\s(.*)",parseTime)
            if parseInterval:
                parseInterval = parseInterval[0]
                if "of" == parseInterval[0]:
                    inte = re.split('\s+', parseInterval[1])
                    #Check the scale
                    if "minutes" in inte[1]:
                        intervalEvent = int(inte[0])
                    elif ("hours" in inte[1]) | ("hour" in inte[1]):
                        intervalEvent = int(inte[0])*60
                    else:
                        return False
                elif "to" == parseInterval[0]:
                    inter = re.findall("(\d+:\d+).*", parseInterval[1])
                    if inter:
                        interEv = parseInterval[1].split(':')
                        intervalEvent = (int(interEv[0])*60 + int(interEv[1]))-(hourEvent*60 + minEvent)
                        if intervalEvent < 0:
                            return False
                    
                    elif ("p.m." in parseInterval[1]) | ("a.m." in parseInterval[1]):
                        inter = re.findall("(\d+)\s(\w\.\w\.)*", parseInterval[1])
                        if inter:
                            inter = inter[0]
                            interEv = int(inter[0])
                            pmam = inter[1]
                            if pmam == "p.m.":
                                interEv = interEv + 12
                                if interEv > 23:
                                    interEv = 0
                                    
                            intervalEvent = (interEv*60) -(hourEvent*60 + minEvent)
                            if intervalEvent < 0:
                                intervalEvent = 60
                        else:
                            return False
                    else: 
                        return False

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

        self.service.events().insert(calendarId=self.calendarId, body=body).execute()

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

    def isEvent(self, text, isOut):
        #Convert text of 'add event' to 'get events' 
        text = text.replace('for', 'of')
        #Delete unnecesary text
        t = re.findall("(the\s|for\sthe\s|this\s)(.+)",text)[0]
        text = ""
        text = text.join(t)

        weekDay = re.findall("(this\s)(\w+)", text)
        if weekDay:
            weekDay = weekDay[0]
            day = weekDay[1]
            dayEvent = self.getWeekDay(day)
            monthEvent = self.dt.strftime('%B').lower()
            #Replace week day for day
            
            text = text.replace(weekDay[0] , "")
            text = text.replace(day, str(dayEvent) + " of " + monthEvent + " at 8 a.m.")
                
        #Get event to check if is saved
        events = self.getEvents(text)
           
        if not isOut:
            if (not events['items']):
                return False
            else: 
                return True
        else:
            if (not events['items']) | ( len(events['items']) != 1):
                return "Not added"
            event = events['items'][0]
            if event:
                dt = parse(event['start']['dateTime'])
                dtf = parse(event['end']['dateTime'])
                textEvent = "Event called: "+event['summary']+" at "+dt.strftime('%A')+", "+str(dt.day)+" of "+dt.strftime('%B')+" at "+dt.strftime('%H')+":"+dt.strftime('%M')+" to "+dtf.strftime('%H')+":"+dtf.strftime('%M')
                textEvent += ". Successfully added"         
                return textEvent                
            else:
                return "Not added"   
        
                    
    def think(self, text):

        if ("add" in text) | ("create" in text) | ("new" in text) | ("remind me" in text):
            if not self.isEvent(text, False):
                if self.setEvents(text):
                    return self.isEvent(text, True)
                else:
                    return "Incorrect input"
            else:
                return "Already one event set"

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
            
                



if __name__ == '__main__':

    if len(sys.argv) == 2:
        text = sys.argv[1]
    else:
        """

        mandatory -> [create a|add a|new] calendar event [called | for] name of the event [for the | the | this] [(["num day"th | "num day"] of month) | this weekday] 
        optional -> at [xx:xx | (xx [p.m. | a.m.])] [to (xx:xx | (xx [p.m. | a.m.])) | (of XX [hours | hour | minutes])
        i.e.
        create a calendar event for meet Melvin the 15th of october at 20:00 to 22:00
        create a calendar event for meet Melvin the 15th of october at 20:00 of 30 minutes
        create a calendar event for meet Melvin the 15th of october at 20:00 
        create a calendar event for meet Melvin the 15 of october at 20:00
        create a calendar event for meet Melvin the 17th of october at 6 p.m. to 8 p.m.
        create a calendar event called my lunch the 17th of october at 6 p.m. of 2 hours.
        add a calendar event for meet Melvin this saturday at 5 p.m.
        new calendar event called holidays this sunday
        
        [list | get | ...] [all the | "" ] calendar events [of this week | of this month | of this day | of "num day" days | of "num day" of month]
        i.e.
        get all the calendar events
        list calendar events of this week
        get calendar events of saturday
        get calendar events of this month
        calendar events of 2 days
        get calendar event of the 17 of october
        
        Same as get events
        i.e.
        
        delete all calendar events
        delete calendar events of this week
        delete calendar events of this saturday
        delete calendar events of this month
        delete calendar event of the 17 of october
        delete calendar events of 2 days
        """
        
        text = "get all calendar events"

    print text + "\n"
    path = os.getcwd()
    calendar = CalendarAPI("/".join(path.split("/")[0:-1]) + "/", False)
    returnedText =  calendar.think(text)
    print returnedText + "\n"



