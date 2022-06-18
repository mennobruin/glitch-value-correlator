import pickle
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from tqdm import tqdm

from application1.handler.data.reader.csv import CSVReader
from application1.model.histogram import Hist
from resources.constants import PLOT_DIR

from virgotools.frame_lib import FrameFile

reader = CSVReader()
triggers = reader.load_csv('GSpy_ALLIFO_O3b_0921_final', usecols=['GPStime', 'peakFreq', 'centralFreq', 'snr'])

t_start = 1264625000
t_stop = 1264635000

triggers = triggers[triggers.GPStime > t_start]
triggers = triggers[triggers.GPStime < t_stop]

mean = 0.0000110343

f_sample = 1000
channel = "V1:ENV_WEB_SEIS_W"
source = '/virgoData/ffl/raw_O3b_arch.ffl'

points = []
with FrameFile(source) as ff:
    for trigger in tqdm(triggers):
        p = ff.getChannel(channel, triggers.GPStime.values[0], 1.2/f_sample).data
        points.append(p)


fig = plt.figure(figsize=(10, 8))
plt.rcParams['font.size'] = 16

plt.scatter(points, triggers.peakFreq, c=np.log10(triggers.snr))
plt.xlabel('Velocity [m/s]')
plt.ylabel('Trigger Frequency [Hz]')
plt.xlim(0, 1.15*max(points))
save_name = f'density_{channel}_peakFreq.png'
fig.savefig(PLOT_DIR + save_name, dpi=fig.dpi)

fig = plt.figure(figsize=(10, 8))
plt.scatter(points, triggers.centralFreq, c=np.log10(triggers.snr))
plt.xlabel('Velocity [m/s]')
plt.ylabel('Trigger Frequency [Hz]')
plt.xlim(0, 1.15*max(points))
save_name = f'density_{channel}_centralFreq.png'
fig.savefig(PLOT_DIR + save_name, dpi=fig.dpi)
