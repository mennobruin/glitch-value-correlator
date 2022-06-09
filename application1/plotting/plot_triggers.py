import os

import numpy as np
import matplotlib.pyplot as plt

from application1.handler.data.reader.csv import CSVReader
# from application1.handler.data.reader.frame_file import FrameFileReader
from resources.constants import RESOURCE_DIR
from application1.handler.triggers import LocalPipeline, Omicron
# from virgotools.frame_lib import FrameFile
from sklearn.manifold import TSNE
import seaborn as sns
import pandas as pd
import pickle as pk

plt.rcParams['font.size'] = 16

source = '/virgoData/ffl/raw_O3b_arch'
file = RESOURCE_DIR + 'csv/GSpy_ALLIFO_O3b_0921_final.csv'
RESULTS_DIR = 'application1/plotting/results/'
reader = CSVReader()
# ffl_reader = FrameFileReader(source=source)
min_start = 1262228200
max_end = 1265825600
triggers = reader.load_csv(file)
# triggers = triggers[triggers.GPStime > min_start]
# triggers = triggers[triggers.GPStime < max_end]
# triggers = triggers.sort_values('snr', ascending=False)

dfs = {}
for _label in set(triggers.label):
    dfs[_label] = triggers[triggers.label == _label]


def ceil_to_nearest_n(num, n):
    frac = num % n
    return num - frac + n


def plot_trigger_density_omicron():
    pipeline = Omicron(channel='V1:ENV_WEB_MAG_N', snr_threshold=10)
    ts, te = 1262678400, 1262908800
    segment_triggers = pipeline.get_segment(gps_start=ts, gps_end=te)

    fig = plt.figure(figsize=(16, 6.4), dpi=300)
    ax = fig.gca()

    bins, locs, _ = ax.hist(segment_triggers, bins=192)
    ax.set_xlim(ts, te)
    ax.set_ylim(0, ceil_to_nearest_n(bins.max(), n=20))
    ax.set_xlabel('GPS Time', labelpad=10)
    ax.set_ylabel('Counts (#)', labelpad=10)
    plt.savefig(RESULTS_DIR + 'trigger_density_omicron.png', dpi=300, transparent=False, bbox_inches='tight')


def plot_trigger_density_labels(trigger):
    pipeline = LocalPipeline(trigger_file=file, trigger_type=trigger)
    labels = list(pipeline.labels)
    ts, te = 1264550418, 1264723218
    segment_triggers = pipeline.get_segment(gps_start=ts, gps_end=te)
    label_triggers = []
    for label in labels[::-1]:
        label_triggers.append((label, segment_triggers[segment_triggers.label == label]))
    label_triggers = sorted(label_triggers, key=lambda x: len(x[1]), reverse=True)

    fig = plt.figure(figsize=(16, 6.4), dpi=300)
    ax = fig.gca()
    cm1 = plt.cm.get_cmap('tab20')
    cm2 = plt.cm.get_cmap('tab20b')
    colors = [cm1(i) for i in np.linspace(0, 1, 20)] + [cm2(i) for i in np.linspace(0, 1, 20)[0:4]]
    bins, locs, _ = ax.hist([t.GPStime for l, t in label_triggers], stacked=True, bins=192, color=colors, label=[l for l, t in label_triggers])
    ax.set_xlim(ts, te)
    ax.set_ylim(0, ceil_to_nearest_n(bins.max(), n=50))
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.45), ncol=4, fancybox=True, shadow=True)
    ax.set_xlabel('GPS Time', labelpad=10)
    ax.set_ylabel('Counts (#)', labelpad=10)
    plt.savefig(RESULTS_DIR + 'trigger_density_labels.png', dpi=300, transparent=False, bbox_inches='tight')


def plot_trigger_times():
    pipeline = LocalPipeline(trigger_file=file)
    triggers = pipeline.get_segment(gps_start=1238680000, gps_end=1262690000)
    times_cutoff = [t % 1 for t in triggers]

    fig = plt.figure(figsize=(8, 6.4), dpi=300)
    ax = fig.gca()

    ax.hist(times_cutoff, bins=100)
    ax.set_xlim(0, 1)
    ax.set_xlabel('Trigger Time (fraction)', labelpad=10)
    ax.set_ylabel('Counts (#)', labelpad=10)
    ax.set_title('Omicron Triggers')
    plt.savefig(RESULTS_DIR + 'trigger_times.png', dpi=300, transparent=False, bbox_inches='tight')
    plt.show()


def plot_trigger_spectrogram(channel, trigger_type, i=0):
    trigger = dfs[trigger_type].iloc[i]
    trigger_time = trigger.GPStime
    duration = trigger.duration
    snr = trigger.snr
    print(f'{trigger_time=}, {duration=}, {snr=}')
    t0 = trigger_time - 3 * duration
    t1 = trigger_time + 3 * duration

    channels = ffl_reader.get_available_channels(trigger_time)
    print([c for c in channels if 'Hrec' in c])

    with FrameFile(source) as ff:
        data = ff.getChannel(channel, t0, t1).data

    fig, ax = plt.subplots()
    plt.specgram(data, Fs=200)
    plt.xlabel('Time')
    plt.ylabel('Frequency')
    ax.set_yscale('log', basey=2)
    plt.title(channel)
    plt.show()


def plot_trigger_distribution_2d():
    exclude = {'GPStime', 'label', 'imgUrl', 'id', 'ifo'}
    new_cols = list(set(triggers.columns) ^ exclude)
    samples = triggers.sample(n=10000)
    data = samples[new_cols].values

    tsne_file = 't_sne.pickle'
    if not os.path.exists(tsne_file):
        tsne = TSNE(n_components=2, learning_rate='auto', init='random', verbose=1)
        embedding = tsne.fit_transform(data)
        with open(tsne_file, 'wb') as f:
            pk.dump(embedding, file=f)
    else:
        with open(tsne_file, 'rb') as f:
            embedding = pk.load(f)
            print(embedding.shape)

    new_df = pd.DataFrame()
    new_df['x'] = embedding[:, 0]
    new_df['y'] = embedding[:, 1]

    plt.figure(figsize=(16, 10))
    sns.scatterplot(
        x='x', y='y',
        data=new_df,
        hue=samples.label,
        palette=sns.color_palette("hls", len(set(samples.label))),
        alpha=0.5
    )
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.savefig(RESULTS_DIR + 't-sne.png', dpi=300, transparent=False, bbox_inches='tight')
    plt.show()


plot_trigger_density_omicron()
# plot_trigger_density_labels(trigger=None)
# plot_trigger_spectrogram(channel='V1:Hrec_hoft_2_200Hz', trigger_type='Scattered_Light')
# plot_trigger_spectrogram(channel='V1:Hrec_hoft_2_200Hz', trigger_type='Scattered_Light', i=-1)
# plot_trigger_times()
# plot_trigger_distribution_2d()
