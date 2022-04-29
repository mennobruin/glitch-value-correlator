import numpy as np

from scipy.stats.distributions import kstwo
from collections import namedtuple

from .base import BaseFOM
from application1.config import config_manager

LOG = config_manager.get_logger(__name__)


KSResult = namedtuple('KSResult', ['d_n', 'p'])


class KolgomorovSmirnov(BaseFOM):

    def __init__(self):
        super(KolgomorovSmirnov, self).__init__()
        self.scores = {}

    def calculate(self, channel, transformation, h_aux, h_trig):
        if h_aux.const_val is None:
            d_n = self._get_statistic(h_aux, h_trig)
            p = self._get_p_value(d_n, h_aux.ntot, h_trig.ntot)
            self.scores[channel, transformation] = KSResult(d_n, p)

    @staticmethod
    def _get_statistic(h_aux, h_trig):
        return np.amax(np.abs(h_aux.cdf - h_trig.cdf))

    @staticmethod
    def _get_p_value(d_n, n1, n2):
        if n1 > n2:
            n = n1 * n2 / (n1 + n2)
        else:
            n = n2 * n1 / (n1 + n2)
        return np.clip(kstwo.sf(d_n, round(n)), 0, 1)
