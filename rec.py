import pyaudio
import numpy
import time
from threading import Lock
from functools import partial
import math

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

MIN_TIME_BETWEEN_CYCLES = 0.1

class Measure(object):
    def __init__(self):
    
        self.peak = False
        self.peak_time = self.last_peak_time = time.time()
        self.peaks = numpy.array([time.time()])
        
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
        distances = self.peaks[1:] - self.peaks[:-1]
        #distances = numpy.append(distances, [time.time() - self.peaks[-1]])
        rpms = 60.0 / distances
        return numpy.average(rpms, weights = math.e ** (self.peaks[1:] - time.time()))

    def callback(self, in_data, frame_count, time_info, status):
        with self.lock:
            a = numpy.fromstring(in_data, dtype=numpy.int16)
            for d in a:
                if d > 30000 and not self.peak:            
                    self.peak = True
                    
                    current_peak_time = time.time()
                    time_between_cycles = current_peak_time - self.peak_time
                    print time_between_cycles
                    if time_between_cycles < MIN_TIME_BETWEEN_CYCLES:
                        continue
                    self.peak_time = current_peak_time
                    self.peaks = numpy.append(self.peaks, [self.peak_time])
                    
                elif d < 20000 and self.peak:
                    self.peak = False
        return (None, pyaudio.paContinue)



    
