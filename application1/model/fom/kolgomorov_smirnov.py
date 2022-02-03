import numpy as np

from .base import BaseFOM


class KolgomorovSmirnov(BaseFOM):

    def __init__(self):
        super(KolgomorovSmirnov, self).__init__()
        self.scores = {}

    def calculate(self, channel, h_aux, h_trig):
        self.scores[channel] = np.amax(np.abs(h_aux.cdf - h_trig.cdf))
