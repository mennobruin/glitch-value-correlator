import pickle
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from application1.handler.data.reader.csv import CSVReader
from application1.model.histogram import Hist
from resources.constants import PLOT_DIR

reader = CSVReader()
triggers = reader.load_csv('GSpy_ALLIFO_O3b_0921_final', usecols=['label'])
labels = set(triggers['label'].values)

t_start = 1264625000
t_stop = 1264635000

test_file = f'test_seis_w_1264625000_1264635000_f50.pickle'
with open(test_file, 'rb') as pkf:
    data = pickle.load(pkf)
    h_trig_cum = data['trig']
    h_aux_cum = data['aux']
    available_channels = data['channels']


transformation = ""
for k in h_aux_cum.keys():
    if k[1] == transformation:
        channel = k[0]
        break

h_aux = h_aux_cum[channel, transformation]
h_trig = Hist(np.array([]))
for label in labels:
    h_trig += h_trig_cum[channel, transformation, label]

h_aux.align(h_trig)

h1, e1 = np.histogram(h_aux.xgrid, weights=h_aux.counts, bins=h_aux.nbin)
h2, e2 = np.histogram(h_trig.xgrid, weights=h_trig.counts, bins=h_trig.nbin)

fig = plt.figure(figsize=(8, 6.4), dpi=300)
plt.rcParams['font.size'] = 16
# plt.bar(h_aux.xgrid, h_aux.counts, width=h_aux.span / h_aux.nbin)
# plt.bar(h_trig.xgrid, h_trig.counts, width=h_trig.span / h_trig.nbin)

x = np.linspace(e1.min(), e1.max())

middle1 = (e1[:-1] + e1[1:])/2
samples1 = [[middle1[i]] * val for i, val in enumerate(h1)]
samples1 = [sample for bar in samples1 for sample in bar]

middle2 = (e2[:-1] + e2[1:])/2
samples2 = [[middle2[i]] * val for i, val in enumerate(h2)]
samples2 = [sample for bar in samples2 for sample in bar]

rkde1 = stats.gaussian_kde(samples1)
rkde2 = stats.gaussian_kde(samples2)

y1, y2 = rkde1.pdf(x), rkde2.pdf(x)

plt.plot(x, y1, '-', label='aux')
plt.plot(x, y2, '-', label='trig')

plt.fill_between(x, y1, alpha=0.3)
plt.fill_between(x, y2, alpha=0.3)

plt.xlim([h_aux.offset, h_aux.offset + h_aux.span])
plt.ylim(0, 1.05*np.max(y1))
plt.xlabel('x')
plt.ylabel('Density')
plt.title(f'{channel} Density')
plt.legend()
save_name = f'density_{channel}_{transformation}.png'
fig.savefig(PLOT_DIR + save_name, dpi=fig.dpi, transparent=False, bbox_inches='tight')
