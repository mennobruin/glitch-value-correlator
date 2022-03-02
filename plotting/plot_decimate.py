import matplotlib.pyplot as plt
import h5py
import pathlib
import os
import re
import numpy as np

from virgotools.frame_lib import FrameFile

source='/virgoData/ffl/raw_O3b_arch'
resource_path = str(pathlib.Path(__file__).parents[1].resolve()) + '/application1/resources/'
ds_path = resource_path + 'ds_data/'
data_path = ds_path + 'data/'

files = os.listdir(data_path)
f = files[3]
with h5py.File(data_path + f, 'r') as hf:
    frames = list(hf.keys())
    channel = frames[0]
    frame = hf.get(channel)

    i = 5
    data = np.array(frame[i])

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

