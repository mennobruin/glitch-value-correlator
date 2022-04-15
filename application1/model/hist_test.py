import numpy as np
import matplotlib.pyplot as plt
from histogram import Hist


def merge(a, b):
    def extract_vals(hist):
        values = [[y] * x for x, y in zip(hist[0], hist[1])]
        return [z for s in values for z in s]

    def extract_bin_resolution(hist):
        return hist[1][1] - hist[1][0]

    def generate_num_bins(minval, maxval, bin_resolution):
        # Generate number of bins necessary to satisfy assumption 2
        return int(np.ceil((maxval - minval) / bin_resolution))

    vals = extract_vals(a) + extract_vals(b)
    bin_resolution = min(map(extract_bin_resolution, [a, b]))

    print(a[0].size)
    return np.histogram(vals, bins=a[0].size)


def test():
    x = np.array([[0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.2, 0.2, 0.3, 0.5, 0.5, 0.5, 0.5] for _ in range(10)]).flatten()
    y = np.array([[0.3, 0.3, 0.3, 0.4, 0.4, 0.4, 0.5, 0.5, 0.6, 0.6, 0.7, 0.8, 0.8, 0.8, 0.8] for _ in range(10)]).flatten()

    l2_nbin = 4
    nbin = 2 ** l2_nbin

    hist1 = Hist(x, l2_nbin=l2_nbin)
    hist2 = Hist(y, l2_nbin=l2_nbin)

    hist3 = np.histogram(x, bins=nbin)
    hist4 = np.histogram(y, bins=nbin)

    hist1 += hist2

    h = hist1
    plt.bar(h.xgrid, h.counts, width=h.span / h.nbin)
    plt.xlim([h.offset, h.offset + h.span])
    plt.show()

    hist, bins = merge(hist3, hist4)
    width = bins[1] - bins[0]
    center = (bins[:-1] + bins[1:]) / 2
    plt.bar(center, hist, align='center', width=width)
    plt.show()


test()
