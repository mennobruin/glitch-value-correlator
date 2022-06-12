import matplotlib.pyplot as plt
import numpy as np

from tqdm import tqdm

from virgotools.frame_lib import FrameFile
from ligo.segments import segment

from application1.handler.data.reader.h5 import H5Reader
from application1.handler.triggers import Omicron, LocalPipeline

RESULTS_DIR = 'application1/plotting/results/'
source = '/virgoData/ffl/trend.ffl'
# source = '/virgoData/ffl/raw_O3b_arch.ffl'

# channels = [
#     ('V1:INF_WEB_CHILLER_TE_IN', 'Temperature (°C)'),
#     ('V1:INF_WEB_CHILLER_PRES_IN', 'Pressure (bar)'),
#     ('V1:INF_WEB_CHILLER_PRES_OUT', 'Pressure (bar)'),
#     ('V1:INF_WEB_CHILLER_TE_OUT', 'Temperature (°C)'),
#     ('V1:INF_WEB_CHILLER_CURR', 'Current (A)')
# ]
#
# channels = [
#     ('V1:ENV_WEB_SEIS_W', r'Velocity ($ms^{-1}$)'),
#     ('V1:SBE_SWEB_GEO_GRWE_raw_500Hz', 'Voltage (V)'),
#     ('V1:SBE_SWEB_act_ty_500Hz', r'$\mu$rad'),
#     ('V1:ENV_WEB_SEIS_N', r'Velocity ($ms^{-1}$)'),
#     ('V1:Sa_WE_F0_TZ_500Hz', 'Voltage (V)')
# ]

channels = [
    ('V1:ENV_WEB_SEIS_W_50Hz_rms_0.03_0.1Hz', r'Velocity ($ms^{-1}$)'),
    ('V1:ENV_WEB_SEIS_W_50Hz_rms_0.1_1Hz', r'Velocity ($ms^{-1}$)'),
    ('V1:ENV_WEB_SEIS_W_50Hz_rms_1_5Hz', r'Velocity ($ms^{-1}$)'),
    ('V1:ENV_WEB_SEIS_W_50Hz_rms_5_15Hz', r'Velocity ($ms^{-1}$)'),
    ('V1:ENV_WEB_SEIS_W_rms', r'Velocity ($ms^{-1}$)'),
    ('V1:ENV_WEB_SEIS_N_50Hz_rms_0.03_0.1Hz', r'Velocity ($ms^{-1}$)'),
    ('V1:ENV_WEB_SEIS_N_50Hz_rms_0.1_1Hz', r'Velocity ($ms^{-1}$)'),
    ('V1:ENV_WEB_SEIS_N_50Hz_rms_1_5Hz', r'Velocity ($ms^{-1}$)'),
    ('V1:ENV_WEB_SEIS_N_50Hz_rms_5_15Hz', r'Velocity ($ms^{-1}$)'),
    ('V1:ENV_WEB_SEIS_N_rms', r'Velocity ($ms^{-1}$)'),
]

target = 'V1:ENV_WEB_MAG_N'

# ts, te = 1262685618, 1262908800
ts, te = 1264550418, 1264723218
# ts, te = 1264610000, 1264670000
f_target = 50
# pipeline = Omicron(channel=target, snr_threshold=20)
pipeline = LocalPipeline(trigger_file='GSpy_ALLIFO_O3b_0921_final.csv')
triggers = pipeline.get_segment(ts, te)
# reader = H5Reader(gps_start=ts, gps_end=te)


def plot(channel, gs, ge, ylabel=None):
    fig = plt.figure(figsize=(20, 6.4))
    ax1 = fig.gca()
    ax2 = ax1.twinx()
    with FrameFile(source) as ff:
        data = ff.getChannel(channel, gs, ge).data
    # data = reader.get_data_from_segments(request_segment=segment(gs, ge), channel_name=channel)
    ax2.hist(triggers.GPStime, bins=192, color='g', alpha=0.4)
    ax1.plot(np.linspace(gs, ge, data.shape[0]), data, '-')
    # for trigger in triggers:
    #     plt.axvline(x=trigger, linestyle='--', color='red')
    plt.xlim(gs, ge)
    plt.title(channel)
    ax1.set_xlabel('GPS Time', labelpad=10)
    if ylabel:
        ax1.set_ylabel(ylabel, labelpad=10)
        ax2.set_ylabel('Trigger Counts (#)', labelpad=10)
    plt.savefig(RESULTS_DIR + f'channel_triggers_{channel}_{ts}_{te}.png', dpi=300, transparent=False,
                bbox_inches='tight')


plt.rcParams['font.size'] = 16

for c, u in tqdm(channels):
    plot(channel=c, gs=ts, ge=te, ylabel=u)
