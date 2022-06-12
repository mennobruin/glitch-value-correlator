import matplotlib.pyplot as plt

from tqdm import tqdm

from virgotools.frame_lib import FrameFile

from application1.handler.triggers import Omicron

RESULTS_DIR = 'application1/plotting/results/'
source = '/virgoData/ffl/trend.ffl'

channels = ['V1:INF_WEB_CHILLER_TE_IN',
            'V1:INF_TB_UPS_TE',
            'V1:INF_TUNNEL_N_TE',
            'V1:INF_NEB_TUNNEL_LUX',
            'V1:SWEB_B8_QD2_H_mean',
            'V1:SNEB_B7_Cam1_PosY_mean',
            'V1:ENV_PCAL_WEB_TE2',
            'V1:ENV_TCS_CO2_NI_TE',
            'V1:ENV_TCS_CO2_WI_DUMP_TE']

target = 'V1:ENV_WEB_MAG_N'

# ts, te = 1262685618, 1262908800
ts, te = 1262690000, 1262700000
pipeline = Omicron(channel=target, snr_threshold=20)
triggers = pipeline.get_segment(ts, te)


def plot(channel, gs, ge):
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
    plt.savefig(RESULTS_DIR + f'channel_triggers_{channel}_{ts}_{te}.png', dpi=300, transparent=False, bbox_inches='tight')


for c in tqdm(channels):
    plot(channel=c, gs=ts, ge=te)
