import matplotlib.pyplot as plt
import numpy as np

np.random.seed(3)

n = 1000
x = np.linspace(0, 1, n)
y = np.zeros(n)

for i in range(0, n - 1):
    y[i + 1] = y[i] + np.random.normal(0, 0.3)

plt.plot(x, y, '-')
plt.axhline(y=0)
plt.show()
