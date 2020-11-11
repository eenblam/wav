#!/usr/bin/env python3

# Inspired by http://blog.acipo.com/wave-generation-in-python/
# and https://www.instagram.com/direct.to.wav/

import itertools, wave, struct, math, random

sample_rate = 44100.0 # hertz
length_seconds = 60
lindex = sample_rate * length_seconds

volume = 32767.0

tone_g4 = 392.00
tone_a4 = 440.00
tone_c5 = 523.25
tone_a6 = 1760.00

#bass_notes = itertools.cycle([tone_g4, tone_a4, tone_c5, tone_a4])
def gen_bass_notes(tones):
    """Random walk through provided list of tones"""
    i = 0
    while True:
        yield tones[i]
        i = (i + random.randint(-1,1)) % len(tones)

bass_notes = gen_bass_notes([tone_g4, tone_a4, tone_c5, tone_a4])
current_note = bass_notes.__next__()

class Wav():
    def __init__(self, filename):
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

def unity(*args):
    n = len(args)
    return sum(args) / n

def bass_gate(t):
    s = sample_rate
    g = 0 < t < s/4 or (s/2 <= t < 5*s/8) or (3*s/4 <= t < 7*s/8)
    return int(g)

def bass_envelope(t):
    # 4bps = 240bpm
    bps = 4
    interval = sample_rate / bps


    residue = pow(t, 1, int(interval))
    return ((interval - residue) / interval)

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

def interp_pairs(t, xs, duration):
    # I think this gets sloppy on the last block,
    # in the sense that it won't fully interpolate.
    # Could update it to detect that we're in a (short) last block
    # and adjust the block_size used for block_ratio accordingly.
    # It's a trade-off:
    # do you want the *rate* your inputs define, or do you want to ultimately reach your final input?

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

def fade_in(t, attack_len, exp=1):
    if t >= attack_len:
        return 1
    return (1 - ((attack_len - t)) / attack_len) ** exp

def fade_out(t, release_len, exp=1):
    begin = lindex - release_len
    if t < begin:
        return 1
    return ((lindex - t) / release_len) ** exp

def run(wav):
    rate = float(sample_rate)
    for i in range(int(length_seconds * sample_rate)):
        # Amplitude modulation over 2s. cos and sin to phase shift A and C amplitudes.
        amp1 = volume * (math.cos(math.pi * float(i) / rate) + 0.5) / 2
        amp2 = volume * (math.sin(2 * math.pi * float(i) / rate) + 0.5) / 2

        # Really slow rise in modulation over course of track
        hum_mod = ((i / lindex) ** 4) * pow(i, 1, 10)
        hum = math.cos((tone_c5 + hum_mod) * math.pi * float(i) / rate)

        x,y = interp_pairs(i, [(2,100), (10,100), (10,10), (10,100), (2,100)], lindex)
        lead_mod = pow(i, int(x), int(y))
        lead = math.cos((tone_a6 + lead_mod) * math.pi * float(i) / rate)
        # Exponential fade in over 6s
        lead_attack = fade_in(i, 6 * sample_rate, 2)

        bass = volume * math.cos(bass_note(i) * math.pi * float(i) / rate)
        beat_pos = pow(i, 1, int(sample_rate))
        env = bass_envelope(beat_pos)

        mix_fade_out = fade_out(i, 10 * sample_rate, 0.75)
        l = mix_fade_out * unity(1.2 * hum * amp1, lead_attack * 0.8 * lead * amp2, env * bass)
        r = mix_fade_out * unity(1.2 * hum * amp2, lead_attack * 0.8 * lead * amp1, env * bass)
        wav.write(l, r)

def main():
    wav = Wav('first.wav')
    run(wav)
    wav.close()

if __name__ == '__main__':
    main()
