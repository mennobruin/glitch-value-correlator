import matplotlib.pyplot as plt

from virgotools.frame_lib import FrameFile

from application1.handler.triggers import Omicron

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

ts, te = 1262685618, 1262908800
pipeline = Omicron(channel=target, snr_threshold=10)
triggers = pipeline.get_segment(ts, te)


def plot(channel, gs, ge):
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    with FrameFile(source) as ff:
        unsampled_data = ff.getChannel(channel, gs, ge).data
    ax2.hist(triggers, bins=100)
    ax1.plot(range(gs, ge), unsampled_data, '-')
    plt.xlim(gs, ge)
    plt.show()


plot(channel=channels[0], gs=ts, ge=te)
