#!/usr/bin/python
import pyttsx, time

class TTSEngine:
    def __init__(self,language='en'):
        self.engine = pyttsx.init()
        self.engine.setProperty('rate', 150)

    def say(self,phrase):
        if self.engine.isBusy() == False:
            self.engine.say(phrase)
            self.engine.runAndWait()

if __name__ == '__main__':
    engine = TTSEngine()
    engine.say("This is a debuging test")
