#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from assets import stt, tts, mic, brain

if __name__ == '__main__':

<<<<<<< HEAD
    stt = stt.STTEngine()
    tts = tts.TTSEngine()
    mic = mic.Microphone()

    wolfram_id='4X2W9X-AGA34L6QWQ'
    client = wolframalpha.Client(wolfram_id)

while True:

    if mic.passiveListen("ok Google"):
        os.system("sox -d voice.flac silence 1 0.1 5% 1 1.0 5%")
        query = stt.transcript('voice.flac')
        print query
        res = client.query(query)
        if len(res.pods) > 0:
            pod = res.pods[1]
            tts.say(pod.text)
        else:
            tts.say("I have no answer for that")
=======
    #Instantiates stt and tts
    stt = stt.STTEngine()
    tts = tts.TTSEngine()
    #Instantiates microphone
    mic = mic.Microphone()
    #Instantiates brain module
    brain = brain.Brain()

    #main loop
    while True:
        #check if ok Google has been said
        if mic.passiveListen("ok Google"):
            # record and process commnad
            os.system("sox -d voice.flac silence 1 0.1 5% 1 1.0 5%")
            query = stt.transcript()
            print query
            if query != "":
                response = brain.think(query)
            else:
                response = "I didn't hear you"
            print response
	    tts.say(response)

>>>>>>> f0af97d0442702cb56fed62cb96b08222dddde06

            



		

		

		



		


