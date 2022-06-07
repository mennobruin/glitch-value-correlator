import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import copy as cp


from application1.model.histogram import Hist
from application1.plotting.plot import plot_histogram_cdf, plot_histogram
from resources.constants import PLOT_DIR

np.random.seed(3)


def find_nearest_index(array, value):
    return np.abs(array - value).argmin()


x1 = np.random.normal(loc=0, scale=1, size=10000)
x2 = np.random.normal(loc=1, scale=1, size=200)
h1 = Hist(x1, l2_nbin=10)
h2 = Hist(x2, l2_nbin=10)
h1_cp = cp.deepcopy(h1)
h2_cp = cp.deepcopy(h2)
h1_cp += h2_cp

i_min = find_nearest_index(h1_cp.cdf, 0.01)
i_max = find_nearest_index(h1_cp.cdf, 0.99)

h1.align(h2)

fig = plot_histogram(histogram=h1, channel="Normal Distribution", transformation="", data_type="test", label=r"$\mu = 0, \sigma = 1$", return_fig=True)
plot_histogram(histogram=h2, channel="Normal Distribution", transformation="", data_type="test", label=r"$\mu = 1, \sigma = 1$", fig=fig, save=True)

fig = plot_histogram_cdf(histogram=h1, channel="Normal Distribution", transformation="", data_type="test", label=r"$\mu = 0, \sigma = 1$", return_fig=True)
# plt.axvline(x=h1_cp.xgrid[i_min], color='k', linestyle='--')
# plt.axvline(x=h1_cp.xgrid[i_max], color='k', linestyle='--')
plot_histogram_cdf(histogram=h2, channel="Normal Distribution", transformation="", data_type="test", label=r"$\mu = 1, \sigma = 1$", fig=fig, save=True)

fig = plt.figure(figsize=(10, 8), dpi=300)
plt.plot(h1_cp.xgrid[::-1], 100 * h1.cdf, '-', label=r"$\mu = 0, \sigma = 1$",)
plt.plot(h1_cp.xgrid[::-1], 100 * (1-h2.cdf), '-', label=r"$\mu = 1, \sigma = 1$",)
plt.plot(h1_cp.xgrid[::-1], 100 * ((1-h2.cdf) - (1-h1.cdf)), '-', label=r"$\Delta$")
plt.xlim(min(h1_cp.xgrid), max(h1_cp.xgrid))
plt.xlabel("x")
plt.ylabel("% vetoed")
plt.legend()
plt.title("Normal Distribution")
save_name = f'test_normal_cdf.png'
fig.savefig(PLOT_DIR + save_name, dpi=fig.dpi)

