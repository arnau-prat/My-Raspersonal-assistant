import pyaudio
import struct
import math
import wave
import urllib  
import urllib2 
import stt

class Microphone:

    def rms(self,frame):
        count = len(frame)/2
        format = "%dh"%(count)
        shorts = struct.unpack( format, frame )

        sum_squares = 0.0
        for sample in shorts:
            n = sample * (1.0/32768.0)
            sum_squares += n*n
        rms = math.pow(sum_squares/count,0.5);

        return rms * 1000

    def passiveListen(self,persona):

        RATE = 16000
        CHUNK = 1024
        THRESHOLD =50
        LISTEN_TIME = 3

        all =[]

        p = pyaudio.PyAudio()

        stream = p.open(format=pyaudio.paInt16,
                             channels=1,
                             rate=RATE,
                             input=True,
                             frames_per_buffer=CHUNK)

        didDetect = False

        for i in range(0, RATE / CHUNK * LISTEN_TIME):
            input = stream.read(CHUNK)
            rms_value = self.rms(input)
            if (rms_value > THRESHOLD):
                didDetect = True
                print "Listening...\n"
                break
        
        if not didDetect:
            stream.stop_stream()
            stream.close()
            return False

        all.append(input)

        for i in range(0, 10):
            data = stream.read(CHUNK)
            all.append(data)

        data = ''.join(all)

        stream.stop_stream()
        stream.close()

        wf = wave.open('/Users/arnauprat/Dropbox/EI/src/12-33.wav', 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(RATE)
        wf.writeframes(data)
        wf.close()

        f = open('/Users/arnauprat/Dropbox/EI/src/12-33.wav')
        audioFile = f.read()
        f.close()
        googl_speech_url = 'https://www.google.com/speech-api/v2/recognize?output=json&lang=en-us&key=AIzaSyCFAEJ8_7dR_9IfeJsTEEfbXQ5hZ0v8CxI'
        hrs = {'Content-type': 'audio/l16; rate=16000'}
        req = urllib2.Request(googl_speech_url, data=audioFile, headers=hrs)
        p = urllib2.urlopen(req)
        rawData = p.read()

        if "okay Google" in rawData:
            return True

        return False
