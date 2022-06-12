import matplotlib.pyplot as plt

from tqdm import tqdm

from virgotools.frame_lib import FrameFile

from application1.handler.triggers import Omicron

RESULTS_DIR = 'application1/plotting/results/'
source = '/virgoData/ffl/trend.ffl'

channels = [
    ('V1:INF_WEB_CHILLER_TE_IN', 'Temperature (°C)'),
    ('V1:INF_WEB_CHILLER_PRES_IN', 'Pressure (bar)'),
    ('V1:INF_WEB_CHILLER_PRES_OUT', 'Pressure (bar)'),
    ('V1:INF_WEB_CHILLER_TE_OUT', 'Temperature (°C)'),
    ('V1:INF_WEB_CHILLER_CURR', 'Current (A)')
    ]

target = 'V1:ENV_WEB_MAG_N'

# ts, te = 1262685618, 1262908800
ts, te = 1262690000, 1262695000
pipeline = Omicron(channel=target, snr_threshold=20)
triggers = pipeline.get_segment(ts, te)


def plot(channel, gs, ge, unit=None):
    fig = plt.figure(figsize=(20, 6.4))
    ax1 = fig.gca()
    ax2 = ax1.twinx()
    with FrameFile(source) as ff:
        unsampled_data = ff.getChannel(channel, gs, ge).data
    # ax1.hist(triggers, bins=100, color='g')
    ax2.plot(range(gs, ge), unsampled_data, '-', alpha=0.6)
    for trigger in triggers:
        plt.axvline(x=trigger, linestyle='--', color='red')
    plt.xlim(gs, ge)
    plt.title(channel)
    plt.xlabel('GPS Time', labelpad=10)
    if unit:
        plt.ylabel(unit, labelpad=10)
    plt.savefig(RESULTS_DIR + f'channel_triggers_{channel}_{ts}_{te}.png', dpi=300, transparent=False,
                bbox_inches='tight')


plt.rcParams['font.size'] = 16

for c, u in tqdm(channels):
    plot(channel=c, gs=ts, ge=te, unit=u)
