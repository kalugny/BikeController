import pyaudio
import numpy
import time
from threading import Lock
from functools import partial

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100


class Measure(object):
    def __init__(self):
    
        self.peak = False
        self.peak_time = self.last_peak_time = time.time()
        self.rpm = 0
        
        self.lock = Lock()
        
        #callback_with_self = partial(self.callback, self)
        
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT,
                                channels=CHANNELS,
                                rate=RATE,
                                input=True,
                                frames_per_buffer=CHUNK,
                                stream_callback=self.callback)

    def start(self):
        print("* recording")
        self.stream.start_stream()
        
    def stop(self):
        print("* done recording")
        self.stream.stop_stream()
        self.stream.close()
        
    def __del__(self):
        self.p.terminate()
        
    def get_rpm(self):
        with self.lock:
            return self.rpm

    def callback(self, in_data, frame_count, time_info, status):
        with self.lock:
            a = numpy.fromstring(in_data, dtype=numpy.int16)
            for d in a:
                if d > 30000 and not self.peak:            
                    print time.time()
                    self.peak = True
                    self.last_peak_time = self.peak_time
                    self.peak_time = time.time()
                    rotation_duration = self.peak_time - self.last_peak_time
                    self.rpm = 60.0 / rotation_duration        
                elif d < -30000 and self.peak:
                    self.peak = False
        return (None, pyaudio.paContinue)



    
