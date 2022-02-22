import matplotlib.pyplot as plt
import h5py
import pathlib
import os
import re

from virgotools.frame_lib import FrameFile

source='/virgoData/ffl/raw_O3b_arch'
resource_path = str(pathlib.Path(__file__).parents[1].resolve()) + '/application1/resources/'
ds_path = resource_path + 'ds_data/'
data_path = ds_path + 'data/'

files = os.listdir(data_path)
f = files[3]
with h5py.File(data_path + f, 'r') as hf:
    all_channels = hf.get('channels')
    all_data = hf.get('data')

    i = 3
    channel_name = all_channels[i]
    data = all_data[i]

    gs, ge = tuple(int(s) for s in re.split('(\d+)', f) if s.isnumeric())

    with FrameFile(source) as ff:
        unsampled_data = ff.getChannel(channel_name, gs, ge).data
        plt.plot(range(len(unsampled_data)), unsampled_data)
        plt.show()

    plt.plot(range(len(data)), data)
    plt.show()

