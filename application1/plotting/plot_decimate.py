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

files = os.listdir(data_path)
f = 'excavator_f50_gs1265655600_ge1265655700_mean.h5'  # files[3]
with h5py.File(data_path + f, 'r') as hf:
    frames = list(hf.keys())
    channel = frames[frames.index("V1:EDB_B1p_PC_AdcMaxVal")]
    # channel = frames[300]
    frame = hf.get(channel)
    data = np.array(frame)

    print(channel)
    print(tuple(int(s) for s in re.split('(\d+)', f) if s.isnumeric()))
    f_sample, gs, ge, _ = tuple(int(s) for s in re.split('(\d+)', f) if s.isnumeric())

    with FrameFile(source) as ff:
        unsampled_data = ff.getChannel(channel, gs, ge).data
        plt.title(channel)
        plt.plot(range(len(unsampled_data)), unsampled_data)
        plt.show()

    plt.title(channel)
    plt.plot(range(len(data)), data)
    plt.show()

