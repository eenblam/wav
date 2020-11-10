#!/usr/bin/env python3

import itertools, wave, struct, math, random

sample_rate = 44100.0 # hertz
length_seconds = 20
lindex = sample_rate * length_seconds

#amplitude = 32767.0
volume = 16383.0

tone_g4 = 392.00
tone_a4 = 440.00
tone_c5 = 523.25
tone_a6 = 1760.00

def gen_bass_notes(tones):
    """Random walk through provided list of tones"""
    i = 0
    while True:
        yield tones[i]
        i = (i + random.randint(-1,1)) % len(tones)

bass_notes = gen_bass_notes([tone_g4, tone_a4, tone_c5, tone_a4])
current_note = bass_notes.__next__()
#bass_notes = itertools.cycle([tone_g4, tone_a4, tone_c5, tone_a4])

class Wav():
    def __init__(self, filename):
        self.name = filename
        self.file = wave.open(filename, 'w')
        self.file.setnchannels(2) # stereo
        self.file.setsampwidth(2) # sample width in bytes. 2 bytes for a short.
        self.file.setframerate(sample_rate)

    def close(self):
        #self.file.writeframes(b'\x00\x00\x00\x00')
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

def unity(*args):
    n = len(args)
    return sum(args) / n

def bass_envelope(t):
    # 4bps = 240bpm
    bps = 4
    interval = sample_rate / bps

    residue = pow(t, 1, int(interval))
    attack = interval / 25.0
    if residue < attack:
        return 1 - ((attack - residue) / attack)
    return ((interval - residue) / interval) ** 1.5

def bass_note(t):
    # Chop to 8s bar
    bar_size = sample_rate * 8
    bar_pos = pow(t, 1, int(bar_size))

    # Alternate a4 and g4
    # First half
    #if bar_pos < sample_rate * 4:
    #    return tone_a4
    #return tone_g4

    # Random walk
    global current
    if bar_pos % (sample_rate / 4) == 0:
        current = bass_notes.__next__()
    return current

def fade_in(t, attack_len, start=0, exp=1):
    t -= start
    # fade-in isn't scheduled yet
    if t < 0:
        return 0
    # fade-in complete
    if t >= attack_len:
        return 1
    # mid-fade-in
    return (1 - ((attack_len - t)) / attack_len) ** exp

def run(wav):
    rate = float(sample_rate)

    dtime = int(rate / 2.5)
    dbuff = [0] * dtime
    w_head = 0
    r_head = 1
    decay = 0.8
    delay = 0
    for i in range(int(length_seconds * sample_rate)):
        bass = volume * math.cos(bass_note(i) * math.pi * float(i) / rate)
        beat_pos = pow(i, 1, int(sample_rate))
        env = bass_envelope(beat_pos)
        bass_out = env * bass

        # Wait 3s, then fade in delay over 5s
        if i > 3 * rate:
            delay = dbuff[r_head] * fade_in(i, 5*rate, start=3*rate)

        dbuff[w_head] = bass_out * decay
        w_head = (w_head + 1) % dtime
        r_head = (r_head + 1) % dtime

        l = unity(bass_out, delay)
        r = unity(bass_out, delay)
        wav.write(l, r)

def main():
    wav = Wav('delay.wav')
    run(wav)
    wav.close()

if __name__ == '__main__':
    main()
