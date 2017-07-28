#!/usr/bin/python

import os
import tempfile
import subprocess
import ttsReq

class TTSEngine:

    def __init__(self,language='en'):
        self.language = language
    
    def play(self,filename):             
        cmd = ['mpg123', str(filename)]
        with tempfile.TemporaryFile() as f:
            subprocess.call(cmd, stdout=f, stderr=f)
            f.seek(0)
            output = f.read()
            print output

    def say(self,phrase):
        tts = ttsReq.TTSRequest(phrase, self.language)
        with tempfile.NamedTemporaryFile(suffix='.http', delete=False) as f:
            tmpfile = f.name
            tts.save(tmpfile)
            self.play(tmpfile)
            print tmpfile
            os.remove(tmpfile)
       
if __name__ == '__main__':
    engine = TTSEngine()
    engine.say("This is a debuging test")
