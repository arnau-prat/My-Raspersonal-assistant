#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import urllib  
import urllib2 
import simplejson as json 



class STTEngine:

    def __init__(self,language='en-us',apiKey='AIzaSyCFAEJ8_7dR_9IfeJsTEEfbXQ5hZ0v8CxI'):
        """
        Initiates the Google STT engine
        """
        self.language = language
        self.apiKey = apiKey

    def transcript(self,audioName):
        f = open(audioName)
        audioFile = f.read()
        f.close()
        googl_speech_url = 'https://www.google.com/speech-api/v2/recognize?output=json&lang='+self.language+'&key='+self.apiKey
        hrs = {'Content-type': 'audio/x-flac; rate=44100'}
        req = urllib2.Request(googl_speech_url, data=audioFile, headers=hrs)
        p = urllib2.urlopen(req)
        rawData = p.read()
        print rawData
        textFileClean = rawData.replace("""{"result":[]}""", '')
        data = json.loads(textFileClean)
        parsedData = data['result'][0]['alternative'][0]['transcript'] 
        os.remove('voice.flac')
        return parsedData

if __name__ == '__main__':

    stt = STTEngine()

    os.system("sox -d voice.flac silence 1 0.1 5% 1 1.0 5%")
    
    print stt.transcript('voice.flac')

  

