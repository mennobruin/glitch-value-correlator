import numpy as np
import matplotlib.pyplot as plt
import random
import cProfile
from scipy.stats import gaussian_kde, norm
from sklearn.neighbors import KernelDensity


def test():
    x = np.array([[0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.2, 0.2, 0.3, 0.5, 0.5, 0.5, 0.5] for i in range(10)]).flatten()
    # x = np.concatenate([norm(-1, 1.).rvs(400), norm(1, 0.3).rvs(100)])
    x_grid = np.linspace(-1, 2, 5000)

    bw = len(x_grid) ** (-1/4 + len(x))
    print(bw)
    kde = KernelDensity(kernel="gaussian", bandwidth=0.05).fit(x[:, np.newaxis])
    log_pdf = kde.score_samples(x_grid[:, np.newaxis])

    plt.plot(x_grid, np.exp(log_pdf), color='red', alpha=0.6, lw=3)
    plt.show()


test()
