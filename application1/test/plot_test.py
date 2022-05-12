import numpy as np

def anderson_darling(a, b):
    m = len(a)
    n = len(b)
    s = 2 * m * n / (m + n)
    a = np.sort(a)
    b = np.sort(b)
    i = 0
    j = 0
    ad = 0.0
    while i < m and j < n:
        if a[i] <= b[j]:
            ad = ad + i / s - (i + 1) / s
            i += 1
        else:
            ad = ad + j / s - (j + 1) / s
            j += 1

    while i < m:
        ad = ad + i / s - (i + 1) / s
        i += 1

    while j < n:
        ad = ad + j / s - (j + 1) / s
        j += 1

    return ad


def anderson_darling2(a,b):
    from scipy import stats
    from numpy import vstack

    ab = vstack([a, b])
    return stats.anderson_ksamp(ab)


if __name__ == "__main__":

    a = np.random.uniform(0, 1, 100)
    b = np.random.uniform(0, 1, 100)

    print(anderson_darling(a, b))
    print(anderson_darling2(a, b))