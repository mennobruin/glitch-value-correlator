import numpy as np
import pickle
import matplotlib.pyplot as plt
plt.rcParams['font.size'] = 16
import os

from application1.model.fom import AndersonDarling
from application1.plotting.plot import plot_histogram_cdf

t_start = 1262649600
t_stop = 1262655700
RESULTS_DIR = 'results/'

test_file = f'../../test_{t_start}_{t_stop}.pickle'
if os.path.exists(test_file):
    with open(test_file, 'rb') as pkf:
        data = pickle.load(pkf)
        h_trig_cum = data['trig']
        h_aux_cum = data['aux']
        channels_transformations = list(h_trig_cum.keys())


fom_ad = AndersonDarling()

def anderson_darling(h1, h2):
    d_n = fom_ad._get_distances(h1, h2)
    combined = fom_ad._combine_hist(h1, h2)
    combined_ecdf = combined.cdf * (1 - combined.cdf)
    ad = np.sum(np.divide(d_n, combined_ecdf, out=np.zeros_like(d_n), where=combined_ecdf != 0))
    ad /= combined.ntot
    return d_n, combined_ecdf, combined


def test_anderson_darling():
    for channel, transformation in channels_transformations:
        h_aux = h_aux_cum[channel, transformation]
        h_trig = h_trig_cum[channel, transformation]
        result = fom_ad.calculate(channel, transformation, h_aux, h_trig)
        if result and result.below_critical:
            h_aux_cp = h_aux.cdf.copy()

            distances, ecdf, combined_hist = anderson_darling(h1=h_aux, h2=h_trig)
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


test_anderson_darling()
