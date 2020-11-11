#!/usr/bin/env python3

import wave, struct

class Wav():
    def __init__(self, filename, sample_rate=44100.0):
        self.name = filename
        self.file = wave.open(filename, 'w')
        self.file.setnchannels(2) # stereo
        self.file.setsampwidth(2) # sample width in bytes. 2 bytes for a short.
        self.file.setframerate(sample_rate)

    def close(self):
        self.file.writeframes(b'\x00')
        self.file.close()

    def write(self, l, r):
        try:
            self.file.writeframesraw( struct.pack('<hh', int(l), int(r) ) )
        except struct.error as e:
            print(e)
            print('l: {} int(l): {}'.format(l, int(l)))
            print('r: {} int(r): {}'.format(r, int(r)))
            raise e

