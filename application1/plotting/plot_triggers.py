import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.size'] = 16

from application1.handler.data.reader.csv import CSVReader
from application1.handler.data.reader.frame_file import FrameFileReader
from resources.constants import RESOURCE_DIR
from application1.handler.triggers import DefaultPipeline
from virgotools.frame_lib import FrameFile

source = '/virgoData/ffl/raw_O3b_arch'
file = RESOURCE_DIR + 'csv/GSpy_ALLIFO_O3b_0921_final.csv'
RESULTS_DIR = 'results/'
reader = CSVReader()
ffl_reader = FrameFileReader()
triggers = reader.load_csv(file)
triggers = triggers.sort_values('snr', ascending=False)

dfs = {}
for _label in set(triggers.label):
    dfs[_label] = triggers[triggers.label == _label]
# min_start = 1262228200
# max_end = 1265825600


def plot_trigger_density(trigger):
    pipeline = DefaultPipeline(trigger_file=file, trigger_type=trigger)
    triggers = pipeline.get_segment(gps_start=1262680000, gps_end=1262690000)
    # triggers = pipeline.triggers
    print(f'{triggers.size} triggers found')
    plt.hist(triggers, bins=100)
    plt.show()


def plot_trigger_times():
    pipeline = DefaultPipeline(trigger_file=file)
    triggers = pipeline.get_segment(gps_start=1238680000, gps_end=1262690000)
    times_cutoff = [t % 1 for t in triggers]

    fig, ax = plt.subplots(1, 1)

    ax.hist(times_cutoff, bins=100)
    ax.set_xlim(0, 1)
    ax.set_xlabel('Trigger Time (fraction)', labelpad=10)
    ax.set_ylabel('Counts (#)', labelpad=10)
    plt.savefig(RESULTS_DIR + 'trigger_times.png', dpi=300, transparent=False, bbox_inches='tight')
    plt.show()


def plot_trigger_spectrogram(channel, trigger_type, i=0):
    trigger = dfs[trigger_type].iloc[i]
    trigger_time = trigger.GPStime
    duration = trigger.duration
    print(trigger_time, duration)
    t0 = trigger_time - 3 * duration
    t1 = trigger_time + 3 * duration

    channels = ffl_reader.get_available_channels(trigger_time)
    print([c for c in channels if 'Hrec_hoft' in c])

    # with FrameFile(source) as ff:
    #     data = ff.getChannel(channel, t0, t1).data
    #
    # fig, ax = plt.subplots()
    # plt.specgram(data, Fs=200)
    # plt.xlabel('Time')
    # plt.ylabel('Frequency')
    # ax.set_yscale('log', basey=2)
    # plt.title(channel)
    # plt.show()


# plot_trigger_density(trigger='Scattered_Light')
plot_trigger_spectrogram(channel='V1:Hrec_hoft_2_200Hz', trigger_type='Scattered_Light')
plot_trigger_spectrogram(channel='V1:Hrec_hoft_2_200Hz', trigger_type='Scattered_Light', i=-1)
# plot_trigger_times()
