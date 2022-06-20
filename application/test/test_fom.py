import numpy as np

from application.model.histogram import Hist, plot_hist
from application.model.fom import KolgomorovSmirnov, AndersonDarling
from application.plotting.plot import plot_histogram_cdf


def test_ks(size):
    x1 = np.random.normal(size=size)
    h1 = Hist(x1, l2_nbin=10)

    x2 = np.random.normal(loc=1, size=size//10)
    h2 = Hist(x2, l2_nbin=10)

    fom_ks = KolgomorovSmirnov()
    h1 += h2
    plot_hist(h1)
    fom_ks.calculate("", "", h1, h2)
    cdf_fig = plot_histogram_cdf(histogram=h1,
                                 channel="",
                                 transformation="",
                                 data_type='h1',
                                 return_fig=True)
    plot_histogram_cdf(histogram=h2,
                       channel="",
                       transformation="",
                       data_type='h2',
                       fig=cdf_fig)

    print(fom_ks.scores)


def test_ad(size):
    x1 = np.random.normal(size=size)
    h1 = Hist(x1, l2_nbin=10)

    x2 = np.random.normal(loc=1, size=size//10)
    h2 = Hist(x2, l2_nbin=10)

    fom_ad = AndersonDarling()
    h1 += h2
    plot_hist(h1)
    fom_ad.calculate("", "", h1, h2)
    cdf_fig = plot_histogram_cdf(histogram=h1,
                                 channel="",
                                 transformation="",
                                 data_type='h1',
                                 return_fig=True)
    plot_histogram_cdf(histogram=h2,
                       channel="",
                       transformation="",
                       data_type='h2',
                       fig=cdf_fig)

    print(fom_ad.scores)


# test_ks(size=16384)
test_ad(size=16384)
