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

def interp_pairs(t, xs, duration):
    # I think this gets sloppy on the last block,
    # in the sense that it won't fully interpolate.
    # Could update it to detect that we're in a (short) last block
    # and adjust the block_size used for block_ratio accordingly.
    # It's a trade-off: currently we maintain a consistent linear rate

    # xs should be a list of m pairs
    # Giving n=m-1 blocks between m indices into the duration, with last at end
    n = len(xs) - 1
    # Float division to divide as evenly as possible
    block_size = float(duration) / n
    # This becomes an index into xs, so need an int
    block = int(t / block_size)
    # using % here since pow() requires an int and we aren't doing crypto
    block_pos = t % block_size
    block_ratio = block_pos / block_size
    # Linear (could try others) interpolation between values at each end of block
    x1,y1 = xs[block]
    x2,y2 = xs[block+1]
    x3 = x1 * (1 - block_ratio) + x2 * block_ratio
    y3 = y1 * (1 - block_ratio) + y2 * block_ratio
    return x3, y3

def run(wav):
    rate = float(sample_rate)
    for i in range(int(length_seconds * sample_rate)):
        # Every 2 seconds. Divide volume in half and shift up by one.
        a1 = volume * (math.cos(math.pi * float(i) / rate) + 0.5) / 2
        a2 = volume * (math.sin(2 * math.pi * float(i) / rate) + 0.5) / 2
        ey = math.cos(tone_c * math.pi * float(i) / rate)
        x,y = interp_pairs(i, [(2,100), (10,100), (10,10), (10,100), (2,100)], lindex)
        see = math.cos((tone_a + pow(i,int(x),int(y))) * math.pi * float(i) / rate)

        low_ey = volume * math.cos(bass_note(i) * math.pi * float(i) / rate)

        beat_pos = pow(i, 1, int(sample_rate))
        env = bass_envelope(beat_pos)

        l = unity(ey * a1, see * a2, env * low_ey)
        r = unity(ey * a2, see * a1, env * low_ey)
        wav.write(l, r)

def main():
    wav = Wav('first.wav')
    run(wav)
    wav.close()

if __name__ == '__main__':
    main()
