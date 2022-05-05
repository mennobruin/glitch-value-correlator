import numpy as np
import matplotlib.pyplot as plt

from application1.handler.data.reader.csv import CSVReader
from resources.constants import RESOURCE_DIR
from application1.handler.triggers import DefaultPipeline
from virgotools.frame_lib import FrameFile

source = '/virgoData/ffl/raw_O3b_arch'
file = RESOURCE_DIR + 'csv/GSpy_ALLIFO_O3b_0921_final.csv'
reader = CSVReader()
triggers = reader.load_csv(file)

# min_start = 1262228200
# max_end = 1265825600


def plot_trigger_density(trigger):
    pipeline = DefaultPipeline(trigger_file=file, trigger_type=trigger)
    triggers = pipeline.get_segment(gps_start=1262680000, gps_end=1262690000)
    # triggers = pipeline.triggers
    print(f'{triggers.size} triggers found')
    plt.hist(triggers, bins=100)
    plt.show()


def plot_trigger_spectrogram(channel, trigger_type):
    trigger = triggers.loc[triggers['label'] == trigger_type][0]
    print(trigger)
    duration = trigger.duration
    t0 = trigger - duration
    t1 = trigger + duration

    with FrameFile(source) as ff:
        data = ff.getChannel(channel, t0, t1).data
        plt.title(channel)


# plot_trigger_density(trigger='Scattered_Light')
plot_trigger_spectrogram(channel='', trigger_type='Scattered_Light')
