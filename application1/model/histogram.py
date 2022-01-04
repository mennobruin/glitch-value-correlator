import numpy as np


class Histogram:

    def __init__(self, x: np.ndarray, nbins: int):
        self.x = x
        self.nbins = nbins
        self.x_size = x.size

