import pickle
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from application1.handler.data.reader.csv import CSVReader
from application1.model.histogram import Hist

reader = CSVReader()
triggers = reader.load_csv('GSpy_ALLIFO_O3b_0921_final', usecols=['label'])
labels = set(triggers['label'].values)

transformation_combinations = [
    [],
    # [GaussianDifferentiator],
    # [HighPass]
]

join_names = lambda c: '_'.join(t.NAME for t in c)
transformation_names = [join_names(t) for t in transformation_combinations]

t_start = 1264625000
t_stop = 1264635000

test_file = f'test_seis_w_1264625000_1264635000_f50.pickle'
with open(test_file, 'rb') as pkf:
    data = pickle.load(pkf)
    h_trig_cum = data['trig']
    h_aux_cum = data['aux']
    available_channels = data['channels']


for k in h_aux_cum.keys():
    if k[1] == '':
        channel = k[0]
        break
transformation = ""

h_aux = h_aux_cum[channel, transformation]
h_trig = Hist(np.array([]))
for label in labels:
    h_trig += h_trig_cum[channel, transformation, label]

h_aux.align(h_trig)

h1, e1 = np.histogram(h_aux.xgrid, weights=h_aux.counts, bins=h_aux.nbin)
h2, e2 = np.histogram(h_trig.xgrid, weights=h_trig.counts, bins=h_trig.nbin)

plt.figure(figsize=(8, 6))
plt.bar(h_aux.xgrid, h_aux.counts, width=h_aux.span / h_aux.nbin)
plt.bar(h_trig.xgrid, h_trig.counts, width=h_trig.span / h_trig.nbin)

x = np.linspace(e1.min(), e1.max())

samples1 = np.random.choice((e1[:-1] + e1[1:])/2, size=h_aux.ntot, p=h1/h1.sum())
samples2 = np.random.choice((e2[:-1] + e2[1:])/2, size=h_trig.ntot, p=h2/h2.sum())
rkde1 = stats.gaussian_kde(samples1)
rkde2 = stats.gaussian_kde(samples2)

y1, y2 = rkde1.pdf(2), rkde2.pdf(x)

plt.plot(x, y1, '-')
plt.plot(x, y2, '-')

plt.fill_between(x, y1, alpha=0.3)
plt.fill_between(x, y2, alpha=0.3)

plt.xlim([h_aux.offset, h_aux.offset + h_aux.span])
plt.show()
