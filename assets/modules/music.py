#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import signal
import subprocess

class Music:
	
	def play(self):
		name = "/home/pi/Desktop/sugar.mp3"
	        self.player = subprocess.Popen(["mplayer", name, "-ss", "30"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		return "Playing music"

	def stop(self):
		self.player.stdin.write("q")
