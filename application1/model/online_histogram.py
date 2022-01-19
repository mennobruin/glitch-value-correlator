import numpy as np


class Bin:

    def __init__(self, p, m):
        self.p = p
        self.m = m

    def __eq__(self, other):
        return self.p == other.p

    def __lt__(self, other):
        return self.p < other.p


class OnlineHistogram:

    def __init__(self, x: np.ndarray, n_bins: int):
        self.x = x
        self.bins = {}
        self.n_bins = n_bins
        self.empty_bins = n_bins

        self._init_hist()

    def _init_hist(self):
        """
        Creates a histogram of B bins with each bin having m points centered around a point p.
        """
        for p in self.x:
            if p in self.bins.keys():
                self.bins[p] += 1

            else:
                self.bins[p] = 1
                
    def __add__(self, other):
        assert other.bins.size == self.n_bins

        combined_hist = self.bins + other.bins
        sorted_combined_hist = sorted(combined_hist)
        self._trim(hist=sorted_combined_hist)

    def _trim(self, hist):
        pass


if __name__ == '__main__':
    a = np.arange(0, 10, 0.01)
    b = np.arange(5, 15, 0.01)

    n = 100
    h1 = OnlineHistogram(x=a, n_bins=n)
    h2 = OnlineHistogram(x=b, n_bins=n)

    h1 += h2
