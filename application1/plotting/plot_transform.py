import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, filtfilt, savgol_filter

n = 5000
dx = 1 / n
xmin, xmax = -2*np.pi, 2*np.pi
x = np.linspace(xmin, xmax, n)
y = np.sin(x)
noise = np.random.normal(size=n)
y += noise

fs = 50
f_nyq = fs / 2
b, a = butter(N=3, Wn=2 * 2/fs, fs=fs)
y_filter = filtfilt(b, a, y)

y_deriv = np.gradient(y_filter, np.linspace(xmin, xmax, n), edge_order=2)

plt.plot(x, y, '-')
plt.plot(x, y_filter, '-', color='orange')
plt.plot(x, y_deriv, '-', color='yellow')
plt.xlim(min(x), max(x))
plt.show()
