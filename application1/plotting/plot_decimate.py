import matplotlib.pyplot as plt
import h5py
import os
import re
import numpy as np

from resources.constants import RESOURCE_DIR
from virgotools.frame_lib import FrameFile
plt.rcParams['font.size'] = 16

source = '/virgoData/ffl/raw_O3b_arch'
ds_path = RESOURCE_DIR + 'ds_data/'
data_path = ds_path + 'data/'
RESULTS_DIR = 'application1/plotting/results/'

channels = ['V1:SUSP_SBE_LC_elapsed_time',
            'V1:PAY_WI_Cam_ProcessingTime']

files = os.listdir(data_path)
f = 'excavator_f50_gs1262649700_ge1262649800_mean.h5'  # files[3]
with h5py.File(data_path + f, 'r') as hf:
    frames = list(hf.keys())
    for c in channels:
        # fig, axes = plt.subplots()
        plt.figure(figsize=(10, 8), dpi=300)
        channel = frames[frames.index(c)]
        frame = hf.get(channel)
        data = np.array(frame)

        print(channel)
        print(tuple(int(s) for s in re.split('(\d+)', f) if s.isnumeric()))
        f_sample, gs, ge, _ = tuple(int(s) for s in re.split('(\d+)', f) if s.isnumeric())

        with FrameFile(source) as ff:
            unsampled_data = ff.getChannel(channel, gs, ge).data
            # axes[0].set_title(channel)
            # axes[0].plot(range(len(unsampled_data)), unsampled_data)
            t0, t1 = 0, 10
            plt.plot(np.linspace(t0, t1, len(unsampled_data)), unsampled_data)
            plt.xlim(t0, t1)
            plt.xlabel(f'Time since gps={gs} [s]')
            plt.ylabel('[arb. unit]')
            plt.title(channel)
            plt.savefig(RESULTS_DIR + f'{channel}_{gs}.png', dpi=300, transparent=False, bbox_inches='tight')

        # axes[1].set_title(channel)
        # axes[1].plot(range(len(data)), data)
        plt.show(block=False)
    plt.show()
