import os

import wolframalpha

from client import stt, tts, mic

if __name__ == '__main__':

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

            



		

		

		



		


