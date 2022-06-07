import numpy as np

from scipy.stats import anderson_ksamp
from collections import namedtuple

from .base import BaseFOM
from application1.config import config_manager

LOG = config_manager.get_logger(__name__)

ADResult = namedtuple('ADResult', ['ad', 'below_critical'])


class AndersonDarling(BaseFOM):
    CRITICAL_VALUES = {0.01: 3.857, 0.05: 2.492, 0.10: 1.933}

    def __init__(self, alpha=0.05):
        super(AndersonDarling, self).__init__()
        self.critical_value = self.CRITICAL_VALUES[alpha]
        self.scores = {}

    def calculate(self, channel, transformation, h_aux, h_trig):
        if h_aux.const_val is None:
            d_n = self._get_distances(h_aux=h_aux, h_trig=h_trig)
            combined = self._combine_hist(h_aux, h_trig)
            combined_ecdf = combined.cdf * (1 - combined.cdf)
            print(1, sum(combined_ecdf))
            ad = np.sum(np.divide(d_n, combined_ecdf, out=np.zeros_like(d_n), where=combined_ecdf != 0))
            ad /= combined.ntot
            result = ADResult(ad, ad < self.critical_value)
            self.scores[channel, transformation] = result
            return result

    @staticmethod
    def _get_distances(h_aux, h_trig):
        return np.abs(h_aux.cdf - h_trig.cdf)

    @staticmethod
    def _combine_hist(h1, h2):
        h1 += h2
        return h1
