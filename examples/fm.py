#!/usr/bin/env python3

# Importing is frustrating.
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from wav import Wav
from wav import unity, interp_pairs
from wav import tones as tone

import itertools, math

sample_rate = 44100.0 # hertz
length_seconds = 60
lindex = sample_rate * length_seconds

volume = 32767.0

bass_notes = itertools.cycle([tone.G4, tone.A4, tone.C5, tone.A4])
current_note = bass_notes.__next__()

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

    global current
    if bar_pos % (sample_rate / 4) == 0:
        current = bass_notes.__next__()
    return current

def run(wav):
    rate = float(sample_rate)
    for i in range(int(length_seconds * sample_rate)):
        # Amplitude modulation over 2s. cos and sin to phase shift A and C amplitudes.
        amp1 = volume * (math.cos(math.pi * float(i) / rate) + 0.5) / 2
        amp2 = volume * (math.sin(2 * math.pi * float(i) / rate) + 0.5) / 2

        # Really slow rise in modulation over course of track
        hum_mod = ((i / lindex) ** 4) * pow(i, 1, 10)
        hum = math.cos((tone.C5 + hum_mod) * math.pi * float(i) / rate)

        x,y = interp_pairs(i, [(2,100), (10,100), (10,10), (10,100), (2,100)], lindex)
        lead_mod = pow(i, int(x), int(y))
        lead = math.cos((tone.A6 + lead_mod) * math.pi * float(i) / rate)

        bass = volume * math.cos(bass_note(i) * math.pi * float(i) / rate)
        beat_pos = pow(i, 1, int(sample_rate))
        env = bass_envelope(beat_pos)

        l = unity(1.2 * hum * amp1, 0.8 * lead * amp2, env * bass)
        r = unity(1.2 * hum * amp2, 0.8 * lead * amp1, env * bass)
        wav.write(l, r)

def main():
    wav = Wav('fm.wav')
    run(wav)
    wav.close()

if __name__ == '__main__':
    main()
