import sys
import collections


class Bin:

    __slots__ = ["left", "right", "center", "count"]

    def __init__(self, left, right, count=0):
        self.left = left
        self.right = right
        self.center = (left + right) / 2
        self.count = count

    def __iadd__(self, other):
        if other.left < self.left:
            self.left = other.left
        if other.right > self.right:
            self.right = other.right
        self.count += other.count
        return self

    def __lt__(self, other):
        return self.right < other.left

    def __eq__(self, other):
        return self.center == other.center


class Histogram(collections.UserList):
    def __init__(self, max_bins):
        super(Histogram, self).__init__()
        self.max_bins = max_bins
        self.n_samples = 0

    def update(self, sample):
        self.n_samples += 1

        sample_bin = Bin(left=sample, right=sample, count=1)

        if not self:
            self.append(sample_bin)
            return self

        low, high = 0, len(self)
        i = (low + high) // 2
        while low < high:
            if self[i] < sample_bin:
                low = i + 1
            else:
                high = i
            i = (low + high) // 2

        if i == len(self):
            self.append(sample_bin)
        else:
            if sample >= self[i].left:
                self[i].count += 1
            else:
                self.insert(i, sample_bin)

        if len(self) > self.max_bins:
            self._trim()

        return self

    def _trim(self):
        min_delta = sys.maxsize
        min_i = None
        for i in range(len(self)-1):
            delta = self[i+1].center - self[i].center
            if delta < min_delta:
                min_delta = delta
                min_i = i
        self[min_i] += self.pop(min_i + 1)


if __name__ == '__main__':
    import numpy as np
    import matplotlib.pyplot as plt
    hist = Histogram(max_bins=512)
    samples = np.random.normal(size=16384)
    for s in samples:
        hist.update(sample=s)

    counts = [b.count for b in hist]
    values = [b.center for b in hist]
    edges = [b.left for b in hist] + [hist[-1].right]
    plt.hist(values, weights=counts, bins=edges)
    plt.show(block=False)

    plt.hist(samples, bins=len(counts), alpha=0.5)
    plt.show()
