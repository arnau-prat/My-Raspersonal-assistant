#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import urllib  
import urllib2 
import simplejson as json 



class STTEngine:

    def __init__(self, language='en', apiKey='AIzaSyCFAEJ8_7dR_9IfeJsTEEfbXQ5hZ0v8CxI'):
        """
        Initiates the Google STT engine
        """
        self.language = language
        self.apiKey = apiKey

<<<<<<< HEAD:client/stt.py
    def transcribe(self, audioName):
=======
    def transcript(self,audioName='voice.flac'):
>>>>>>> f0af97d0442702cb56fed62cb96b08222dddde06:assets/modules/stt.py
        f = open(audioName)
        audioFile = f.read()
        f.close()
        googl_speech_url = 'https://www.google.com/speech-api/v2/recognize?output=json&lang=' + self.language + '&key=' + self.apiKey
        hrs = {'Content-type': 'audio/x-flac; rate=44100'}
        req = urllib2.Request(googl_speech_url, data=audioFile, headers = hrs)
        p = urllib2.urlopen(req)
        rawData = p.read()
        textFileClean = rawData.replace("""{"result":[]}""", '')
<<<<<<< HEAD:client/stt.py
	if textFileClean != "\n":
        	data = json.loads(textFileClean)
        	parsedData = data['result'][0]['alternative'][0]['transcript']
	else:
		parsedData = "" 
        os.remove('voice.flac')
=======
        if textFileClean != '\n':
            data = json.loads(textFileClean)
            parsedData = data['result'][0]['alternative'][0]['transcript']
        else:
            parsedData = "" 
        os.remove(audioName)
>>>>>>> f0af97d0442702cb56fed62cb96b08222dddde06:assets/modules/stt.py
        return parsedData

"""
if __name__ == '__main__':
    stt = STTEngine()
    os.system("sox -d voice.flac silence 1 0.1 5% 1 1.0 5%")
    print stt.transcript('voice.flac')
"""
  

