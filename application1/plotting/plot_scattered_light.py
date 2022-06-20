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
    for t in tqdm(triggers.GPStime):
        p = ff.getChannel(channel, t, 1.2/f_sample).data
        points.append(abs(p - mean))
points = np.array(points)

i_scattered_light = np.flatnonzero(triggers[triggers.label == 'Scattered_Light'])
i_other = np.flatnonzero(triggers[triggers.label != 'Scattered_Light'])

plt.rcParams['font.size'] = 16

# fig = plt.figure(figsize=(10, 8))
# sc = plt.scatter(points, triggers.peakFreq, c=np.log10(triggers.snr), s=5*np.log10(triggers.snr))
# plt.colorbar(sc)
# plt.xlabel('Velocity [m/s]')
# plt.ylabel('Trigger Frequency [Hz]')
# plt.xlim(0, 1.15*max(points))
# plt.ylim(0, 150)
# save_name = f'{channel}_peakFreq.png'
# fig.savefig(PLOT_DIR + save_name, dpi=fig.dpi)
#
# fig = plt.figure(figsize=(10, 8))
# sc = plt.scatter(points, triggers.centralFreq, c=np.log10(triggers.snr), s=5*np.log10(triggers.snr))
# plt.colorbar(sc)
# plt.xlabel('Velocity [m/s]')
# plt.ylabel('Trigger Frequency [Hz]')
# plt.xlim(0, 1.15*max(points))
# plt.ylim(0, 150)
# save_name = f'{channel}_centralFreq.png'
# fig.savefig(PLOT_DIR + save_name, dpi=fig.dpi)
#
# fig = plt.figure(figsize=(10, 8))
# sc = plt.scatter(points, triggers.peakFreq, c=np.log10(triggers.snr), s=5*np.log10(triggers.snr))
# plt.colorbar(sc)
# plt.xlabel('Velocity [m/s]')
# plt.ylabel('Trigger Frequency [Hz]')
# plt.xlim(0, 1.15*max(points))
# save_name = f'density_{channel}_peakFreq.png'
# fig.savefig(PLOT_DIR + save_name, dpi=fig.dpi)
#
# fig = plt.figure(figsize=(10, 8))
# sc = plt.scatter(points, triggers.centralFreq, c=np.log10(triggers.snr), s=5*np.log10(triggers.snr))
# plt.colorbar(sc)
# plt.xlabel('Velocity [m/s]')
# plt.ylabel('Trigger Frequency [Hz]')
# plt.xlim(0, 1.15*max(points))
# save_name = f'density_{channel}_centralFreq.png'
# fig.savefig(PLOT_DIR + save_name, dpi=fig.dpi)

p_scattered_light = points[i_scattered_light]
t_scattered_light = triggers[i_scattered_light]
p_other = points[i_scattered_light]
t_other = triggers[i_scattered_light]

fig = plt.figure(figsize=(10, 8))
plt.scatter(p_other, t_other.peakFreq, s=5*np.log10(t_other.snr), a=0.7)
plt.scatter(p_scattered_light, t_scattered_light.peakFreq, s=5*np.log10(t_scattered_light.snr))
plt.xlabel('Velocity [m/s]')
plt.ylabel('Trigger Frequency [Hz]')
plt.xlim(0, 1.15*max(points))
save_name = f'{channel}_seperate_peakFreq.png'
fig.savefig(PLOT_DIR + save_name, dpi=fig.dpi)

fig = plt.figure(figsize=(10, 8))
plt.scatter(p_other, t_other.centralFreq, s=5*np.log10(t_other.snr), a=0.7)
plt.scatter(p_scattered_light, t_scattered_light.centralFreq, s=5*np.log10(t_scattered_light.snr))
plt.xlabel('Velocity [m/s]')
plt.ylabel('Trigger Frequency [Hz]')
plt.xlim(0, 1.15*max(points))
save_name = f'{channel}_seperate_centralFreq.png'
fig.savefig(PLOT_DIR + save_name, dpi=fig.dpi)
