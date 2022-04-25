"""
references:
 [1] Miller, L. H. (1956). Table of Percentage Points of Kolmogorov Statistics. Journal of the American Statistical
     Association, 51(273), 111–121. https://doi.org/10.2307/2280807
"""

import numpy as np

from scipy.stats import ks_2samp

from .base import BaseFOM


class KolgomorovSmirnov(BaseFOM):

    CRITICAL_COEFFICIENTS = {0.1: 1.22385, 0.05: 1.35810, 0.01: 1.62762, 0.001: 1.94947}  # as seen in [1]

    def __init__(self):
        super(KolgomorovSmirnov, self).__init__()
        self.scores = {}

    def _calculate(self, channel, transformation, h_aux, h_trig):
        try:
            self.scores[channel, transformation] = np.amax(np.abs(h_aux.cdf - h_trig.cdf))
        except AssertionError:
            self.scores[channel, transformation] = 0

    def calculate(self, channel, transformation, h_aux, h_trig):
        # try:
        self.scores[channel, transformation] = ks_2samp(h_trig, h_aux)
        # except np.AxisError:
        #     self.scores[channel, transformation] = 0

    def get_critical_value(self, n1, n2, confidence=0.05):
        return self.CRITICAL_COEFFICIENTS[confidence] * np.sqrt((n1 + n2) / n1 / n2)
