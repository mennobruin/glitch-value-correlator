import pickle
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from application1.handler.data.reader.csv import CSVReader
from application1.model.histogram import Hist
from resources.constants import PLOT_DIR

from virgotools.frame_lib import FrameFile

reader = CSVReader()
triggers = reader.load_csv('GSpy_ALLIFO_O3b_0921_final', usecols=['GPStime', 'label', 'snr'])

t_start = 1264625000
t_stop = 1264635000

triggers = triggers[triggers.GPStime > t_start]
triggers = triggers[triggers.GPStime < t_stop]

mean = 0.0000110343

channel = "V1:ENV_WEB_SEIS_W"
source = '/virgoData/ffl/raw_O3b_arch.ffl'

with FrameFile(source) as ff:
    # for trigger in triggers:
    print(ff.getChannel(channel, triggers[0].GPStime, 1))
