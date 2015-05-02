#!/usr/bin/python

import os
import tempfile
import subprocess
import gtts

class TTSEngine:

    def __init__(self,language='en'):
        """
        Initiates the Google TTS engine
        """
        self.language = language
    
    def play(self,filename):             
        cmd = ['mpg123', str(filename)]
        with tempfile.TemporaryFile() as f:
            subprocess.call(cmd, stdout=f, stderr=f)
            f.seek(0)
            output = f.read()

    def say(self,phrase):
        tts = gtts.gTTS(phrase, self.language)
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            tmpfile = f.name
        tts.save(tmpfile)
        self.play(tmpfile)
        os.remove(tmpfile)
        
"""        
if __name__ == '__main__':
    engine = TTSEngine()
    engine.say("This is a debuging test")
"""