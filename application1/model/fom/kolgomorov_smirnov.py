"""
references:
 [1] Miller, L. H. (1956). Table of Percentage Points of Kolmogorov Statistics. Journal of the American Statistical
     Association, 51(273), 111–121. https://doi.org/10.2307/2280807
"""

import numpy as np

from math import isclose
from scipy.stats import ks_2samp

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
        try:
            ks_result = ks_2samp(h_trig.counts, h_aux.counts)
            self.scores[channel, transformation] = ks_result.statistic, ks_result.pvalue
        except AttributeError:
            self.scores[channel, transformation] = 0, 0

    def get_critical_value(self, n1, n2, confidence=0.05):
        return self.CRITICAL_COEFFICIENTS[confidence] * np.sqrt((n1 + n2) / n1 / n2)
