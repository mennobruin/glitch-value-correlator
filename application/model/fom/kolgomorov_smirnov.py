"""
    Kolmogorov-Smirnov test implementation. Includes bootstrapping.
"""

from collections import namedtuple

import numpy as np
from scipy.stats.distributions import kstwo

from application.config import config_manager
from application.model.histogram import Hist

LOG = config_manager.get_logger(__name__)


KSResult = namedtuple('KSResult', ['d_n', 'std_d_n', 'p', 'std_p'])


class KolmogorovSmirnov:

    def __init__(self):
        super(KolmogorovSmirnov, self).__init__()
        self.scores = {}

    def calculate(self, channel, transformation, h_aux, h_trig, bootstrap=False):
        if h_aux.const_val is None:
            if bootstrap:
                d_n, std_d_n, p, std_p = self.bootstrap(h_aux=h_aux, h_trig=h_trig)
                self.scores[channel, transformation] = KSResult(d_n, std_d_n, p, std_p)
            else:
                d_n = self._get_distance(h_aux, h_trig)
                p = self._get_p_value(d_n, h_aux.ntot, h_trig.ntot)
                self.scores[channel, transformation] = KSResult(d_n, None, p, None)

    @staticmethod
    def _get_distance(h_aux, h_trig):
        return np.amax(np.abs(h_aux.cdf - h_trig.cdf))

    @staticmethod
    def _get_p_value(d_n, n1, n2):
        if n1 > n2:
            n = n1 * n2 / (n1 + n2)
        else:
            n = n2 * n1 / (n1 + n2)
        return np.clip(kstwo.sf(d_n, round(n)), 0, 1)

    def bootstrap(self, h_aux, h_trig, n_cycles=5000):
        np.set_printoptions(threshold=np.inf)

        counts1, dx1 = h_aux.counts, (h_aux.x_max - h_aux.x_min) / h_aux.nbin
        counts2, dx2 = h_trig.counts, (h_trig.x_max - h_trig.x_min) / h_trig.nbin

        bin_edges1 = h_aux.x_min + dx1 * np.arange(h_aux.nbin)
        bin_edges2 = h_trig.x_min + dx2 * np.arange(h_trig.nbin)

        points1 = np.concatenate([
            np.random.uniform(low=edge1, high=edge2, size=counts1[i])
            for i, (edge1, edge2) in enumerate(zip(bin_edges1[0:-1], bin_edges1[1:]))
        ])
        points2 = np.concatenate([
            np.random.uniform(low=edge1, high=edge2, size=counts2[i])
            for i, (edge1, edge2) in enumerate(zip(bin_edges2[0:-1], bin_edges2[1:]))
        ])

        size1 = h_aux.ntot // 5
        size2 = h_trig.ntot // 5
        distances, probabilities = [], []
        for _ in range(n_cycles):
            sample1 = np.random.choice(points1, size=size1, replace=True)
            sample2 = np.random.choice(points2, size=size2, replace=True)

            hist1, _ = np.histogram(sample1, bins=bin_edges1)
            hist2, _ = np.histogram(sample2, bins=bin_edges2)

            cdf1 = hist1.cumsum() / size1
            cdf2 = hist2.cumsum() / size2

            d_n = np.amax(np.abs(cdf1 - cdf2))
            p = self._get_p_value(d_n, size1, size2)

            distances.append(d_n)
            probabilities.append(p)

        return np.mean(distances), np.std(distances), np.mean(probabilities), np.std(probabilities)


if __name__ == '__main__':
    fom = KolmogorovSmirnov()
    n = 485672
    m = 1341
    x = np.random.normal(loc=0, scale=100, size=n)

    h1 = Hist(x[:m], l2_nbin=6)
    h2 = Hist(x[m:], l2_nbin=6, spanlike=h1)

    d, std_d, p, std_p = fom.bootstrap(h_aux=h2, h_trig=h1, n_cycles=100)
    print(f'D_n = {d} +/- {std_d}')
    print(f'P = {p} +/- {std_p}')
