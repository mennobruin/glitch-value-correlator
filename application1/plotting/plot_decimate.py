import matplotlib.pyplot as plt
import h5py
import os
import re
import numpy as np

from resources.constants import RESOURCE_DIR
from virgotools.frame_lib import FrameFile

source = '/virgoData/ffl/raw_O3b_arch'
ds_path = RESOURCE_DIR + 'ds_data/'
data_path = ds_path + 'data/'

channels = ['V1:SUSP_SBE_LC_elapsed_time',]

files = os.listdir(data_path)
f = 'excavator_f50_gs1262649700_ge1262649800_mean.h5'  # files[3]
with h5py.File(data_path + f, 'r') as hf:
    frames = list(hf.keys())
    # for c in channels:
    for i in range(100, 110):
        fig, axes = plt.subplots(2, 1)
        # channel = frames[frames.index(c)]
        channel = frames[i]
        frame = hf.get(channel)
        data = np.array(frame)

        print(channel)
        print(tuple(int(s) for s in re.split('(\d+)', f) if s.isnumeric()))
        f_sample, gs, ge, _ = tuple(int(s) for s in re.split('(\d+)', f) if s.isnumeric())

        with FrameFile(source) as ff:
            unsampled_data = ff.getChannel(channel, gs, ge).data
            axes[0].set_title(channel)
            axes[0].plot(range(len(unsampled_data)), unsampled_data)

        axes[1].set_title(channel)
        axes[1].plot(range(len(data)), data)
        plt.show(block=False)
    plt.show()

