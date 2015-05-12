#!/usr/bin/python
import RPi.GPIO as GPIO


class Light:
    def __init__(self):
        GPIO.setup(21, GPIO.OUT)
        GPIO.output(21, True)

    def switchOn(self):
        GPIO.output(21, False)
        return "turning lights on"

    def switchOff(self):
        GPIO.output(21, True)
        return "turning lights off"

    def thinkLight(self, text):
        if "on" in text:
            response = self.switchOn

        elif "off" in text:
            response = self.switchOff

        else:
            response = "invalid input"


