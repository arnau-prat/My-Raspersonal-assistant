import os

from client import stt, tts, mic

if __name__ == '__main__':

	mic = mic.Microphone()

	stt = stt.STTEngine()
	tts = tts.TTSEngine()

while True:

	if mic.passiveListen("Ok Google"):

		print "Say your command!!!!!!\n"

		os.system ('afplay client/beep.mp3')

		os.system("sox -d voice.flac silence 1 0.1 5% 1 1.0 5%")

		query = stt.transcript('voice.flac')

		tts.say("You said: "+query)


		print query

		



		


