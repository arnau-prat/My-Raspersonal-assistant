#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from assets import stt, tts, mic, brain

if __name__ == '__main__':

    #Instantiates stt and tts
    stt = stt.STTEngine()
    tts = tts.TTSEngine()
    #Instantiates microphone
    mic = mic.Microphone()
    #Instantiates brain module
    brain = brain.Brain(os.getcwd() + "/assets")

    #main loop
    while True:
        #check if ok Google has been said
        if mic.passiveListen("google"):
            # record and process commnad
            os.system("rec --encoding signed-integer --bits 16 --channels 1 --rate 16000 voice.wav silence 1 0.1 5% 1 1.0 5%")
            query = stt.transcript()
            print query
            if query != "":
                response = brain.think(query)
            else:
                response = "I didn't hear you"
            print response
            tts.say(response)


