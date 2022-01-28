import matplotlib.pyplot as plt
from tqdm import tqdm

from application1.utils import *
from application1.model import Segment, Hist, FFLCache
from application1.handler.data import Decimator, DataReader
from application1.handler.triggers import Omicron
from core.config import ConfigurationManager

LOG = ConfigurationManager.get_logger(__name__)


def main(source, channel_name, t_start, t_stop):
    reader = DataReader()
    decimator = Decimator()

    bl_patterns = ['*max', '*min', 'V1:VAC*', 'V1:Daq*', '*rms']
    available_channels = reader.get_available_channels(source, t_start, patterns=bl_patterns)[0:20]
    print(len(available_channels))

    trigger_pipeline = Omicron(channel=available_channels[0])
    trigger_pipeline.get_segment(gps_start=t_start, gps_end=t_stop)

    # segment: Segment = reader.get(channel_name, t_start, t_stop, source=source)
    # segment_50hz: Segment = decimator.decimate(segment, target_frequency=50)
    #
    # aux_data = FFLCache(ffl_file=source, f_target=None, gps_start=t_start, gps_end=t_stop)
    # h_aux, h_trig = construct_histograms(available_channels, segments=aux_data.segments, aux_data=aux_data)
    #
    # h = Hist(segment_50hz.x)
    # plt.bar(h.xgrid, h.counts, width=h.span / h.nbin)
    # plt.xlim([h.offset, h.offset + h.span])
    # plt.show()


def construct_histograms(channels, segments, aux_data):
    h_aux_cum = dict((c, Hist([])) for c in channels)
    h_trig_cum = dict((c, Hist([])) for c in channels)

    for i, seg, gap in iter_segments(segments):
        if gap:
            pass  # todo: when transformations are implemented -> reset

        # todo: access Omicron pipeline for triggers

        LOG.info('Constructing histograms...')
        for channel in tqdm(channels, position=0, leave=True):
            x_aux = aux_data.get_data_from_segment(request_segment=seg, channel=channel)
            # todo: handle non-finite values. Either discard channel or replace values.

            # todo: apply transformations to the data
            # for transform in transformations do ...

            h_aux = Hist(x_aux, spanlike=h_aux_cum[channel])
            print(np.nonzero(h_aux.counts).size)
            h_aux_cum += h_aux

    return h_aux_cum, h_trig_cum


if __name__ == '__main__':
    main(source='/virgoData/ffl/raw_O3b_arch',
         channel_name='V1:Hrec_hoft_2_200Hz',
         t_start=1262228600,
         t_stop=1262228700)
