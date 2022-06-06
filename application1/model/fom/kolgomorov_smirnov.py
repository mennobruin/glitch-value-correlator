import numpy as np
import matplotlib.pyplot as plt

from scipy.stats.distributions import kstwo
from scipy.stats import norm
from collections import namedtuple

from tqdm import tqdm

from application1.model.histogram import Hist
from application1.config import config_manager

LOG = config_manager.get_logger(__name__)


KSResult = namedtuple('KSResult', ['d_n', 'p'])


class KolgomorovSmirnov:

    def __init__(self):
        super(KolgomorovSmirnov, self).__init__()
        self.scores = {}

    def calculate(self, channel, transformation, h_aux, h_trig, bootstrap=False):
        if h_aux.const_val is None:
            if bootstrap:
                d_n, p = self.bootstrap(h_aux=h_aux, h_trig=h_trig)
            else:
                d_n = self._get_distance(h_aux, h_trig)
                p = self._get_p_value(d_n, h_aux.ntot, h_trig.ntot)
            self.scores[channel, transformation] = KSResult(d_n, p)

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

    # @staticmethod
    # def _get_bootstrap_sample_size(p1, p2, significance=0.05, power=0.99):
    #     """
    #     [1] Wang, H. and Chow, S.-C. 2007. Sample Size Calculation for Comparing Proportions. Wiley Encyclopedia of Clinical Trials.
    #     """
    #
    #     z = norm.isf([significance/2]) - norm.isf([power])
    #     delta_mean = abs(np.mean(p1) - np.mean(p2))
    #     std = np.std(np.concatenate([p1, p2]))
    #     return int(2 * std * std * z * z / (delta_mean * delta_mean))

    def bootstrap(self, h_aux, h_trig, n_cycles=100):

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
        print(points1.shape)
        print(points2.shape)

        size1 = h_aux.ntot
        size2 = h_trig.ntot
        print(size1)
        print(size2)
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

        print(distances)
        return np.mean(distances), np.mean(probabilities)


if __name__ == '__main__':
    fom = KolgomorovSmirnov()
    n = 8192
    m = n // 10
    x = np.random.normal(loc=0, scale=100, size=n)

    h1 = Hist(x[:m], l2_nbin=6)
    h2 = Hist(x[m:], l2_nbin=6, spanlike=h1)

    d, p = fom.bootstrap(h_aux=h2, h_trig=h1, n_cycles=100)
    print(f'D_n = {d}')
    print(f'P = {p}')
