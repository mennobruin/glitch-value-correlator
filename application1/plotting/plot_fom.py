import numpy as np
import pickle
import matplotlib.pyplot as plt
import os

from application1.handler.data.reader.csv import CSVReader
from application1.model.fom import AndersonDarling, KolgomorovSmirnov
from application1.model.histogram import Hist
from application1.plotting.plot import plot_histogram_cdf
plt.rcParams['font.size'] = 16

t_start = 1264625000
t_stop = 1264635000
RESULTS_DIR = 'results/'

test_file = f'test_{t_start}_{t_stop}_f50.pickle'
with open(test_file, 'rb') as pkf:
    data = pickle.load(pkf)
    h_trig_cum = data['trig']
    h_aux_cum = data['aux']
    channels_transformations = list(h_aux_cum.keys())

fom_ad = AndersonDarling()


def anderson_darling(h1, h2):
    d_n = fom_ad._get_distances(h1, h2)
    combined = fom_ad._combine_hist(h1, h2)
    combined_ecdf = combined.cdf * (1 - combined.cdf)
    ad = np.sum(np.divide(d_n, combined_ecdf, out=np.zeros_like(d_n), where=combined_ecdf != 0))
    ad /= combined.ntot
    return ad, d_n, combined_ecdf, combined


def test_anderson_darling():
    for channel, transformation in channels_transformations:
        h_aux = h_aux_cum[channel, transformation]
        h_trig = h_trig_cum[channel, transformation]
        result = fom_ad.calculate(channel, transformation, h_aux, h_trig)
        if result and result.below_critical:
            h_aux_cp = h_aux.cdf.copy()

            _, distances, ecdf, combined_hist = anderson_darling(h1=h_aux, h2=h_trig)
            y_values = np.array([min(v) for v in zip(h_aux.cdf, h_trig.cdf)])

            fig = plot_histogram_cdf(histogram=h_aux, channel=channel, transformation=transformation, data_type=r'$\hat{F}$', return_fig=True)
            plot_histogram_cdf(histogram=h_trig, channel=channel, transformation=transformation, data_type=r'$\hat{G}$', fig=fig, return_fig=True)
            # plt.vlines(x=h_aux.xgrid, ymin=y_values, ymax=y_values + distances, lw=1/ecdf/100)
            plt.xlim(min(h_aux.xgrid), max(h_aux.xgrid))
            plt.xlabel('x')
            plt.ylabel('CDF')
            plt.savefig(RESULTS_DIR + 'combined_cdf.png', dpi=300, transparent=False, bbox_inches='tight')
            plt.show()
            plt.figure(figsize=(10, 8), dpi=300)
            plt.plot(h_aux.xgrid, combined_hist.cdf, label=r'$\hat{C}$')
            plt.plot(h_aux.xgrid, ecdf, 'g--', label=r'$\hat{C} (1 - \hat{C})$')
            plt.xlim(min(h_aux.xgrid), max(h_aux.xgrid))
            plt.legend()
            plt.title(channel)
            plt.xlabel('x')
            plt.ylabel('CDF')
            plt.savefig(RESULTS_DIR + 'anderson_darling_combined_cdf.png', dpi=300, transparent=False, bbox_inches='tight')
            plt.show()
            plt.plot(combined_hist.xgrid, combined_hist.cdf - h_aux_cp)
            plt.xlim(min(h_aux.xgrid), max(h_aux.xgrid))
            plt.xlabel('x')
            plt.ylabel(r'$\Delta$ CDF')
            plt.title(channel)
            plt.savefig(RESULTS_DIR + 'anderson_darling_diff_combined_cdf.png', dpi=300, transparent=False, bbox_inches='tight')
            plt.show()
            break


# test_anderson_darling()

def test_bootstrap(h_aux, h_trig, n_cycles=1):

    counts1, dx1 = h_aux.counts, (h_aux.x_max - h_aux.x_min) / h_aux.nbin
    counts2, dx2 = h_trig.counts, (h_trig.x_max - h_trig.x_min) / h_trig.nbin

    bin_edges1 = h_aux.x_min + dx1 * np.arange(h_aux.nbin)
    bin_edges2 = h_trig.x_min + dx2 * np.arange(h_trig.nbin)

    for _ in range(n_cycles):
        points1 = np.concatenate([
            np.random.uniform(low=edge1, high=edge2, size=counts1[i])
            for i, (edge1, edge2) in enumerate(zip(bin_edges1[0:-1], bin_edges1[1:]))
        ])
        points2 = np.concatenate([
            np.random.uniform(low=edge1, high=edge2, size=counts2[i])
            for i, (edge1, edge2) in enumerate(zip(bin_edges2[0:-1], bin_edges2[1:]))
        ])

        sample1 = np.random.choice(points1, size=8192, replace=True)
        sample2 = np.random.choice(points2, size=64, replace=True)

        hist1, bins1 = np.histogram(sample1, bins=bin_edges1)
        hist2, bins2 = np.histogram(sample2, bins=bin_edges2)

        width = (bins1[1] - bins1[0]) * 0.4
        bins_shifted = bins1 + width
        plt.bar(bin_edges1, counts1)
        plt.bar(bins_shifted[:-1], hist1)
        plt.show()


if __name__ == '__main__':
    # n = 8192
    # x = np.random.normal(loc=0, scale=100, size=n)
    #
    # h1 = Hist(x[:32], l2_nbin=6)
    # h2 = Hist(x[32:], l2_nbin=6, spanlike=h1)
    #
    # test_bootstrap(h_aux=h2, h_trig=h1, n_cycles=1)
    channel = "V1:SDB2_B1pP_PD1_VBias"
    transformation = ""

    GPS_TIME = 'GPStime'
    LABEL = 'label'
    reader = CSVReader()
    triggers = reader.load_csv('GSpy_ALLIFO_O3b_0921_final', usecols=[GPS_TIME, LABEL])
    labels = set(triggers[LABEL].values)

    h_aux = h_aux_cum[channel, transformation]
    h_trig = Hist(np.array([]))
    for label in labels:
        h_trig += h_trig_cum[channel, transformation, label]
    ad, *_ = anderson_darling(h_aux, h_trig)
    print(ad)
