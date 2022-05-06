import numpy as np

from scipy.stats import anderson_ksamp
from collections import namedtuple

from .base import BaseFOM
from application1.config import config_manager

LOG = config_manager.get_logger(__name__)


ADResult = namedtuple('ADResult', ['ad', 'below_critical'])


class AndersonDarling(BaseFOM):

    CRITICAL_VALUES = {0.01: 3.857, 0.05: 2.492, 0.10: 1.933}

    def __init__(self):
        super(AndersonDarling, self).__init__()
        self.scores = {}

    def calculate(self, channel, transformation, h_aux, h_trig):
        if h_aux.const_val is None:
            d_n = self._get_distances(h_aux, h_trig)
            combined = self._combine(h_aux, h_trig)
            ad = np.sum(d_n / (combined * (1 - combined)))
            ad /= h_aux.ntot * h_trig.ntot
            self.scores[channel, transformation] = ADResult(ad, ad < self.CRITICAL_VALUES[0.05])

    @staticmethod
    def _get_distances(h_aux, h_trig):
        return np.abs(h_aux.cdf - h_trig.cdf)

    @staticmethod
    def _combine(h1, h2):
        h1 += h2
        return h1.cdf
