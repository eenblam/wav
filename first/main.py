#!/usr/bin/env python2

# Inspired by http://blog.acipo.com/wave-generation-in-python/
# and https://www.instagram.com/direct.to.wav/

import wave, struct, math

sample_rate = 44100.0 # hertz
length_seconds = 30
lindex = sample_rate * length_seconds

#amplitude = 32767.0
volume = 16383.0

tone_a = 1760.00  # A
tone_c =  523.25  # C

class Wav():
    def __init__(self, filename):
        self.name = filename
        self.file = wave.open(filename, 'w')
        self.file.setnchannels(2) # stereo
        self.file.setsampwidth(2) # ???
        self.file.setframerate(sample_rate)

    def close(self):
        self.file.writeframes('')
        self.file.close()

    def write(self, l, r):
        self.file.writeframesraw( struct.pack('<hh', l, r ) )

def unity(*args):
    n = len(args)
    return sum(args) / n

def bass_gate(t):
    s = sample_rate
    g = 0 < t < s/4 or \
            (s/2 <= t < 5 * s / 8) or \
            (3 * s / 4 <= t < 7 * s / 8)
    return int(g)

def bass_envelope(t):
    s = sample_rate
    ratio = 4
    interval = s / 4

    residue = pow(t, 1, int(interval))
    return (interval - residue) / interval

def bass_note(t):
    beat_pos = pow(t, 1, int(sample_rate) * 8)
    if beat_pos < sample_rate * 4:
        return 440
    return 394

def run(wav):
    rate = float(sample_rate)
    for i in range(int(length_seconds * sample_rate)):
        # Every 2 seconds. Divide volume in half and shift up by one.
        a1 = volume * (math.cos(math.pi * float(i) / rate) + 0.5) / 2
        a2 = volume * (math.sin(2 * math.pi * float(i) / rate) + 0.5) / 2
        ey = math.cos(tone_c * math.pi * float(i) / rate)
        #TODO interpolate through these values
        see = math.cos((tone_a + pow(i,2,100)) * math.pi * float(i) / rate)
        #see = math.cos((tone_a + pow(i,10,100)) * math.pi * float(i) / rate)
        #see = math.cos((tone_a + pow(i,10,10)) * math.pi * float(i) / rate)

        k = int(5 * (math.sin(2 * math.pi * float(i) / rate) + 1))
        mod = pow(i, 10, 10 + k)
        #see = math.cos((tone_a + mod) * math.pi * float(i) / rate)

        low_ey = volume * math.cos(bass_note(i) * math.pi * float(i) / rate)

        j = 0
        if lindex / 4.0 < i < lindex * 3.0 / 4:
            j = int(1 * (math.cos(0.2 * math.pi * float(i) / rate) + 1))
        beat_pos = pow(i, 1 + j, int(sample_rate))
        gate = bass_gate(beat_pos)
        env = bass_envelope(beat_pos)

        l = unity(ey * a1, env * see * a2, env * low_ey)
        r = unity(ey * a2, env * see * a1, env * low_ey)
        wav.write(l, r)

def main():
    wav = Wav('first.wav')
    run(wav)
    wav.close()

if __name__ == '__main__':
    main()
