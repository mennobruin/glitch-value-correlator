"""
references:
 [1] Miller, L. H. (1956). Table of Percentage Points of Kolmogorov Statistics. Journal of the American Statistical
     Association, 51(273), 111–121. https://doi.org/10.2307/2280807
"""

import numpy as np

from scipy.stats.distributions import kstwo

from .base import BaseFOM
from application1.config import config_manager

LOG = config_manager.get_logger(__name__)


class KolgomorovSmirnov(BaseFOM):

    CRITICAL_COEFFICIENTS = {0.1: 1.22385, 0.05: 1.35810, 0.01: 1.62762, 0.001: 1.94947}  # as seen in [1]

    def __init__(self):
        super(KolgomorovSmirnov, self).__init__()
        self.scores = {}

    def filter_scores(self, p_threshold=0.05):
        filtered_scores = {k: v for k, v in self.scores.items() if v[1] < p_threshold}
        LOG.debug(f'Filtered out {len(self.scores) - len(filtered_scores)} channels with p-value>{p_threshold:.2f}')
        self.scores = filtered_scores

    def calculate(self, channel, transformation, h_aux, h_trig):
        if h_aux.const_val is None:
            d_n = self._get_statistic(h_aux, h_trig)
            p = self._get_p_value(d_n, h_aux.ntot, h_trig.ntot)
            self.scores[channel, transformation] = d_n, p
        else:
            self.scores[channel, transformation] = 0, 0

    @staticmethod
    def _get_statistic(h_aux, h_trig):
        return np.amax(np.abs(h_aux.cdf - h_trig.cdf))

    @staticmethod
    def _get_p_value(d_n, n1, n2):
        if n1 > n2:
            n = n1 * n2 / (n1 + n2)
        else:
            n = n2 * n1 / (n1 + n2)
        return kstwo.sf(d_n, round(n), cdf=False)

    def get_critical_value(self, n1, n2, confidence=0.05):
        return self.CRITICAL_COEFFICIENTS[confidence] * np.sqrt((n1 + n2) / n1 / n2)
