import pickle
import numpy as np
import matplotlib.pyplot as plt

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

nbin = h_aux.nbin // 128
print(nbin)

plt.hist(h_aux.xgrid[::128], weights=h_aux.counts, bins=nbin, density=True)
plt.hist(h_trig.xgrid[::128], weights=h_trig.counts, bins=nbin, density=True)

plt.xlim([h_aux.offset, h_aux.offset + h_aux.span])
plt.show()
