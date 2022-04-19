import numpy as np
import matplotlib.pyplot as plt


def main():
    a = np.linspace(0, 2*np.pi, 100000)
    b = np.sin(10*a)
    plt.plot(a, b, 'b-')

    b_alias = np.mean(b.reshape(-1, 1000), axis=1)
    a_alias = np.linspace(0, 2*np.pi, len(b_alias))
    plt.plot(a_alias, b_alias, 'r-', linewidth=5)

    b_alias = np.mean(b.reshape(-1, 10), axis=1)
    b_alias = np.mean(b_alias.reshape(-1, 10), axis=1)
    b_alias = np.mean(b_alias.reshape(-1, 10), axis=1)
    a_alias = np.linspace(0, 2*np.pi, len(b_alias))
    plt.plot(a_alias, b_alias, 'g-')

    plt.show()


main()
