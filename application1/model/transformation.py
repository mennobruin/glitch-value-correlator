import numpy as np
import matplotlib.pyplot as plt

from application1.utils import abs_norm
from application1.config import config_manager

LOG = config_manager.get_logger(__name__)


class GaussianDifferentiator:

    def __init__(self, n_points, kernel_n_sigma=2, sigma=1, order=1):
        """

        :param n_points: number of data points in the input signal
        :param kernel_n_sigma: width of the kernel expressed in number of standard diviations
        :param sigma: gaussian standard deviation
        :param order: nd derivative order
        """

        super(GaussianDifferentiator, self).__init__()
        self.n_points = n_points
        self.kernel_width = kernel_n_sigma * sigma
        self.sigma = sigma
        self.kernel = self._get_kernel(order=order)

    def _get_kernel(self, order):
        x = np.linspace(-self.kernel_width, self.kernel_width, self.n_points)
        gauss = np.exp(-0.5 * np.square(x) / np.square(self.sigma))
        if order == 1:
            gauss_derivative = -x / np.square(self.sigma) * gauss
            return abs_norm(gauss_derivative)
        elif order == 2:
            gauss_second_derivative = (np.square(x) - np.square(self.sigma)) / np.power(self.sigma, 4) * gauss
            return abs_norm(gauss_second_derivative)
        else:
            LOG.error(f'Gaussian filter order {order} not implemented. Available options: [1, 2]')
            raise ValueError

    def calculate(self, x):
        return np.convolve(x, self.kernel, mode='same')


class AbsMean:

    def __init__(self, mean=None):
        self.mean = mean
        self.means = []

    def calculate(self, x):
        if not self.mean:
            mean = np.mean(x)
            self.means.append(mean)
        return np.abs(x - mean)

    def reset(self):
        self.mean = None
