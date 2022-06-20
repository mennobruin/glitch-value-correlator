import pickle
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy import stats
from tqdm import tqdm

from application1.handler.data.reader.csv import CSVReader
from application1.model.histogram import Hist
from resources.constants import PLOT_DIR

from virgotools.frame_lib import FrameFile

reader = CSVReader()
triggers = reader.load_csv('GSpy_ALLIFO_O3b_0921_final', usecols=['GPStime', 'peakFreq', 'centralFreq', 'snr', 'label'])

t_start = 1264625000
t_stop = 1264635000

wavelength = 1064E-9

triggers = triggers[triggers.GPStime > t_start]
triggers = triggers[triggers.GPStime < t_stop]

glitch_type = 'Scattered_Light'
i_glitch = triggers.index[triggers.label == glitch_type]
i_other = triggers.index[triggers.label != glitch_type]

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

x_max = 1.15*max(points)
y_max = 1.15*max(triggers.peakFreq)
y = 2 * x_max / wavelength

plt.rcParams['font.size'] = 16

# fig = plt.figure(figsize=(10, 8))
# plt.plot([0, x_max], [0, y], 'k--', label='Single-bounce')
# plt.plot([0, x_max], [0, 2*y], 'k-.', label='Double-bounce')
# sc = plt.scatter(points, triggers.peakFreq, c=np.log10(triggers.snr), s=10*np.log10(triggers.snr), cmap='rainbow')
# cbar = plt.colorbar(sc)
# cbar.set_label(r'log$_{10}$ SNR', rotation=90)
# plt.xlabel('Velocity [m/s]')
# plt.ylabel('Trigger Frequency [Hz]')
# plt.xlim(0, x_max)
# plt.ylim(0, 80)
# plt.legend()
# save_name = f'{channel}_peakFreq.png'
# fig.savefig(PLOT_DIR + save_name, dpi=fig.dpi)

# fig = plt.figure(figsize=(10, 8))
# plt.plot([0, x_max], [0, y], 'k--', label='Single-bounce')
# plt.plot([0, x_max], [0, 2*y], 'k-.', label='Double-bounce')
# sc = plt.scatter(points, triggers.peakFreq, c=np.log10(triggers.snr), s=10*np.log10(triggers.snr), cmap='rainbow')
# cbar = plt.colorbar(sc)
# cbar.set_label(r'log$_{10}$ SNR', rotation=90)
# plt.xlabel('Velocity [m/s]')
# plt.ylabel('Trigger Frequency [Hz]')
# plt.xlim(0, x_max)
# plt.ylim(0, y_max)
# plt.legend()
# save_name = f'density_{channel}_peakFreq.png'
# fig.savefig(PLOT_DIR + save_name, dpi=fig.dpi)

p_glitch = points[i_glitch - 336497]
t_glitch = triggers.loc[i_glitch]
p_other = points[i_other - 336497]
t_other = triggers.loc[i_other]

fig = plt.figure(figsize=(10, 8))
plt.plot([0, x_max], [0, y], 'k--', label='Single-bounce')
plt.plot([0, x_max], [0, 2*y], 'k-.', label='Double-bounce')
plt.scatter(p_other, t_other.peakFreq, s=10*np.log10(t_other.snr), label='Other')
plt.scatter(p_glitch, t_glitch.peakFreq, s=10 * np.log10(t_glitch.snr), label='Scattered Light')
plt.xlabel('Velocity [m/s]')
plt.ylabel('Trigger Frequency [Hz]')
plt.xlim(0, x_max)
plt.ylim(0, 80)
plt.legend()
save_name = f'{channel}_separate_peakFreq_{glitch_type}.png'
fig.savefig(PLOT_DIR + save_name, dpi=fig.dpi)

# fig = plt.figure(figsize=(10, 8))
# plt.plot([0, x_max], [0, y], 'k--', label='Single-bounce')
# plt.plot([0, x_max], [0, 2*y], 'k-.', label='Double-bounce')
# plt.scatter(p_other, t_other.peakFreq, s=5*np.log10(t_other.snr))
# plt.scatter(p_scattered_light, t_scattered_light.peakFreq, s=5*np.log10(t_scattered_light.snr))
# plt.xlabel('Velocity [m/s]')
# plt.ylabel('Trigger Frequency [Hz]')
# plt.xlim(0, x_max)
# plt.ylim(0, y_max)
# plt.legend()
# save_name = f'density_{channel}_seperate_peakFreq.png'
# fig.savefig(PLOT_DIR + save_name, dpi=fig.dpi)
