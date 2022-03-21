import numpy as np
import matplotlib.pyplot as plt

from application1.utils import abs_norm
from application1.config import config_manager

LOG = config_manager.get_logger(__name__)


class GaussianDifferentiator:

    def __init__(self, kernel_width=3, sigma=1, order=1):
        super(GaussianDifferentiator, self).__init__()
        self.kernel_width = kernel_width
        self.sigma = sigma
        self.kernel = self._get_kernel(order=order)

    def _get_kernel(self, order):
        x = np.linspace(-3 * self.sigma, 3 * self.sigma, self.kernel_width)
        gauss = np.exp(-0.5 * np.square(x) / np.square(self.sigma))
        gauss_derivative = -x / np.square(self.sigma) * gauss
        gauss_second_derivative = (np.square(x) - np.square(self.sigma)) / np.power(self.sigma, 4) * gauss
        if order == 1:
            return abs_norm(gauss_derivative)[::-1]  # reverse because convolution, not cross-correlation
        elif order == 2:
            return abs_norm(gauss_second_derivative)[::-1]
        else:
            LOG.error(f'Gaussian filter order {order} not implemented. Available options: [1, 2]')
            raise ValueError

    def calculate(self, x):
        return np.convolve(x, self.kernel, mode='same')

    def reset(self):
        pass


if __name__ == '__main__':
    n = 100
    diff = GaussianDifferentiator(kernel_width=n, order=1)


    xdata = np.linspace(0, 2*np.pi, n)
    sinewave = np.sin(xdata)
    sinediff = diff.calculate(x=sinewave)

    plt.plot(xdata, sinewave, 'r-')
    plt.plot(xdata, sinediff, 'g-')
    plt.show()
