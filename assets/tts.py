#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import tempfile
import subprocess
import gtts
import sys

if sys.platform == 'darwin':
	PLAYER = 'afplay';
else:
	PLAYER = 'mpg123';

class TTSEngine:

    def __init__(self,language='en'):
        """
        Initiates the Google TTS engine
        """
        self.language = language
    
    def play(self,filename):             
<<<<<<< HEAD:client/tts.py
        cmd = [PLAYER, str(filename)]
=======
        cmd = ['mpg321', str(filename)]
>>>>>>> f0af97d0442702cb56fed62cb96b08222dddde06:assets/tts.py
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
<<<<<<< HEAD:client/tts.py

    engine.say("This is a debuging test")
=======
    engine.say("This is a debuging test")
"""
>>>>>>> f0af97d0442702cb56fed62cb96b08222dddde06:assets/tts.py
