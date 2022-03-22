import numpy as np
import scipy.signal as sig
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


class SavitzkyGolayDifferentiator:

    POLYNOMIAL_ORDER = 3
    PADDING_MODE = 'wrap'

    def __init__(self, window_length, order, dx):
        """

        :param window_length: length of the filter window
        :param order: nd derivative order
        :param dx: spacing between samples
        """
        self.window_length = window_length
        self.order = order
        self.dx = dx

    def calculate(self, x):
        return sig.savgol_filter(x, self.window_length,
                                 polyorder=self.POLYNOMIAL_ORDER,
                                 deriv=self.order,
                                 delta=self.dx,
                                 mode=self.PADDING_MODE)


class AbsMean:

    def __init__(self, mean=None):
        """

        :param mean: value to use as offset for the input signal
        """
        self.mean = mean
        self.means = []

    def calculate(self, x):
        if not self.mean:
            mean = np.mean(x)
            self.means.append(mean)
            return np.abs(x - mean)
        else:
            return np.abs(x - self.mean)

    def reset(self):
        self.mean = None


class HighPass:

    FILTER_ORDER = 1
    FREQUENCY_CUTOFF = 2

    def __init__(self, f_target):
        f_nyquist = f_target / 2
        self.B, self.A = sig.butter(self.FILTER_ORDER, self.FREQUENCY_CUTOFF / f_nyquist, btype='highpass')

        self.zi = None

    def calculate(self, x):
        if self.zi is None:
            self.zi = sig.lfiltic(self.B, self.A, [self.B[0] * (x[1] - x[0])], [2 * x[0] - x[1]])
        x_trans, self.zi = sig.lfilter(self.B, self.A, x, zi=self.zi)
        return x_trans

    def reset(self):
        self.zi = None


if __name__ == '__main__':
    n = 5000
    xdata = np.linspace(-np.pi, np.pi, n)
    ydata = np.sin(xdata)

    # trans = SavitzkyGolayDifferentiator(window_length=int(n/2), order=1, dx=xdata[1]-xdata[0])
    # trans = HighPass(f_target=50)
    trans = GaussianDifferentiator(n_points=n)
    ytrans = trans.calculate(ydata)

    plt.plot(xdata, ydata)
    plt.plot(xdata, ytrans)
    plt.show()

