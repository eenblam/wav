#!/usr/bin/env python3

from .helpers import unity

#TODO drop sample_rate
sample_rate = 44100.0 # hertz

#TODO allow feedback to drone
#TODO take a callback for a feedback FX send
#TODO stereo spread
class Delay():
    def __init__(self, decay=0.5, feedback=0, max_delay_time=sample_rate):
        self.max_delay_time = int(max_delay_time)
        self.dtime = self.max_delay_time
        self.dbuff = [0] * self.max_delay_time
        # Managing these separately to enable tape delay later
        self.r_head = 0
        self.w_head = self.max_delay_time - 1
        self.decay = decay
        self.feedback = feedback

    def send(self, signal, feedback=0, delay_time=None):
        if delay_time is not None:
            if delay_time > self.max_delay_time:
                raise ValueError("Delay time {} greater than max delay time {}".format(delay_time, self.max_delay_time))
            self.dtime = int(delay_time)
        if not (0 <= self.feedback <= 1):
            raise ValueError("Feedback ({}) must be between 0 and 1".format(feedback))
        self.feedback = feedback
        out = self.dbuff[self.r_head]
        self.dbuff[self.w_head] *= self.decay
        self.dbuff[self.w_head] += unity(signal, out * self.feedback)
        self.w_head = (self.w_head + 1) % self.max_delay_time
        self.r_head = (self.w_head - self.dtime) % self.max_delay_time
        return out
