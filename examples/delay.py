#!/usr/bin/env python3

# Importing is frustrating.
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import itertools, math

from wav import Wav, Delay, unity
from wav import tones as tone


sample_rate = 44100.0 # hertz
length_seconds = 20
lindex = sample_rate * length_seconds

volume = 32767.0

bass_notes = itertools.cycle([tone.g4, tone.a4, tone.c5, tone.a4])
current_note = bass_notes.__next__()

def bass_envelope(t):
    # 4bps = 240bpm
    bps = 4
    interval = sample_rate / bps

    residue = pow(t, 1, int(interval))
    attack = interval / (100.0 / bps)
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
    #    return tone.a4
    #return tone.g4

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


#TODO match this up with wav.helpers.interp
def interp(t, start=0, end=1, begin_time=0, finish_time=lindex, exp=1):
    length = finish_time - begin_time
    if t < begin_time:
        return start
    if t >= finish_time:
        return end
    weight = ((t - begin_time) / length) ** exp
    return start * (1 - weight) + end * weight


def run(wav):
    rate = float(sample_rate)

    d = Delay(decay=0.15, max_delay_time=rate * 2.5)
    delay = 0
    for i in range(int(length_seconds * sample_rate)):
        bass = volume * math.cos(bass_note(i) * math.pi * float(i) / rate)
        beat_pos = pow(i, 1, int(sample_rate))
        env = bass_envelope(beat_pos)
        bass_out = env * bass

        dt = int(interp(i, start=rate*0.8, end=rate*0.4, begin_time=rate*3, finish_time=rate*7, exp=2))

        # Wait 1s, then fade in delay over 1s
        delay = d.send(bass_out, feedback=0.8, delay_time=dt) * fade_in(i, 1*rate, start=1*rate)
        if i < rate:
            delay = 0

        l = unity(bass_out, 0.8 * delay)
        r = unity(bass_out, 0.8 * delay)
        wav.write(l, r)


def main():
    wav = Wav('delay.wav')
    run(wav)
    wav.close()

if __name__ == '__main__':
    main()
