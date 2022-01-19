import numpy as np


class NewHistogram:

    EPSILON = 1e-7

    def __init__(self, x, l2_nbins=7):
        self.x = x
        self.x_min = x.min()
        self.x_max = x.max()
        self.x_range = self.x_max - self.x_min
        self.n = x.size
        self.dx = self.x_range / self.n
        self.n_bins = 2 ** l2_nbins

        margin = (self.n_bins + 2) / self.n_bins
        self.bin_width = self.x_range / self.n_bins + margin

        self.bin_indices = self._get_bin_index(self.x)
        self.counts = np.bincount(self.bin_indices)
        print(self.counts)
        print(self.counts.size)
        print(np.sum(self.counts))

    def _get_bin_index(self, p):
        return np.floor(((p - self.x_min) / self.x_range) * self.n_bins * (1 - self.EPSILON)).astype(np.uint32)

    @staticmethod
    def _get_scaling_factor(x_range):
        return int(2 ** np.ceil(np.log2(x_range)))

    def __add__(self, other):

        x_max = max(self.x_max, other.x_max)
        x_min = min(self.x_min, other.x_min)
        combined_range = x_max - x_min

        scaling_factor = 1
        if combined_range > self.x_range or combined_range > other.x_range:
            scaling_factor = self._get_scaling_factor(combined_range)


if __name__ == '__main__':

    test_data = np.arange(0.1, 0.7, 0.0001)
    test1 = test_data[:int(0.6 * test_data.size)]
    test2 = test_data[int(0.4 * test_data.size):]

    hist1 = NewHistogram(x=test1)
    hist2 = NewHistogram(x=test2)
    hist1 += hist2
