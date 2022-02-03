import numpy as np

from .base import BaseFOM


class KolgomorovSmirnov(BaseFOM):

    def __init__(self):
        super(KolgomorovSmirnov, self).__init__()

    @staticmethod
    def calculate(h_aux, h_trig):
        return np.amax(np.abs(h_aux.cdf - h_trig.cdf))
