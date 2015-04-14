#!/usr/bin/python
# -*- coding: utf-8 -*-

# gosttpy.py
# Created by: fito_segrera 
# www.fii.to
# 05-07-14



import urllib  # For http request / google search
import urllib2  # For doing https POST
import simplejson as json # for handling JSON objects - in this case the return from google's API
import os


class STTEngine:

    def voiceRecognitionAndSearch(self, apiKey,audioName):
        f = open(audioName)
        audioFile = f.read()
        f.close()
        lang_code = 'en-US'
        googl_speech_url = 'https://www.google.com/speech-api/v2/recognize?output=json&lang=en-us&key=' + apiKey
        hrs = {'Content-type': 'audio/x-flac; rate=16000'}
        req = urllib2.Request(googl_speech_url, data=audioFile, headers=hrs)
        p = urllib2.urlopen(req)

        # -----------------------
        # For some reason the google speech API returns 2 json objects (the first one is empty)
        # and parsing with the json library was breaking the code...
        # I solved the issue writing a .txt file with the json data and deleting the first json object in the stream...
        # As follows:

        rawData = p.read()
    
        # remove the empty "{"result":[]}" object that comes in the json
        # string:
        textFileClean = rawData.replace("""{"result":[]}""", '')
        
        # -----------------------
        # Parsing the CLEAN JSON data:

        # Loads the converted and cleaned data as a JSON object
        data = json.loads(textFileClean)
        parsedData = data['result'][0]['alternative'][0]['transcript'] 

        # This line deletes the audio file once the operation is done
        os.remove('voice.flac')

        return parsedData

if __name__ == '__main__':

    tts = STTEngine()

    os.system("sox -r 16000 -d voice.flac silence 1 0.1 5% 1 1.0 5%")

    print tts.voiceRecognitionAndSearch('AIzaSyCFAEJ8_7dR_9IfeJsTEEfbXQ5hZ0v8CxI','voice.flac')





