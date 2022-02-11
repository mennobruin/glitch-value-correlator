import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import sys

from application1.utils import *
from application1.model import ChannelSegment, Hist, FFLCache
from application1.model.fom import KolgomorovSmirnov
from application1.handler.data import Decimator, DataReader
from application1.handler.triggers import Omicron, DefaultPipeline
from core.config import ConfigurationManager

LOG = ConfigurationManager.get_logger(__name__)


class Excavator:
    EXCLUDE_PATTERNS = ['*max', '*min', 'V1:VAC*', 'V1:Daq*', '*rms']
    FILE_TEMPLATE = 'excavator_f{f_target}_gs{t_start}_ge{t_stop}'

    def __init__(self, source, channel_name, t_start, t_stop, f_target=1, channel_bl_patterns=None):
        self.source = source
        self.channel_name = channel_name
        self.t_start = t_start
        self.t_stop = t_stop
        self.f_target = f_target
        self.resource_path = get_resource_path(depth=0)
        self.ds_data_path = self.resource_path + 'ds_data/'
        print(self.resource_path)

        self.reader = DataReader()

        bl_patterns = channel_bl_patterns if channel_bl_patterns else self.EXCLUDE_PATTERNS
        self.available_channels = self.reader.get_available_channels(source, t_start, exclude_patterns=bl_patterns)[0:20]
        self.n_channels = len(self.available_channels)

    def run(self, n_iter):

        print(len(self.available_channels))

        # trigger_pipeline = Omicron(channel=available_channels[0])
        trigger_pipeline = DefaultPipeline(trigger_file='gspy_O3b_c090_blip')
        triggers = trigger_pipeline.get_segment(gps_start=self.t_start, gps_end=self.t_stop)
        if triggers.size == 0:
            LOG.error(f"No triggers found between {self.t_start} and {self.t_stop}, aborting...")
            sys.exit(1)

        # segment: Segment = reader.get(channel_name, t_start, t_stop, source=source)
        # segment_50hz: Segment = decimator.decimate(segment, target_frequency=50)
        #
        aux_data = FFLCache(ffl_file=self.source, f_target=None, gps_start=self.t_start, gps_end=self.t_stop)
        h_aux_cum, h_trig_cum = self.construct_histograms(channels=self.available_channels,
                                                          aux_data=aux_data,
                                                          segments=aux_data.segments,
                                                          triggers=triggers)

        print(h_aux_cum)
        print(h_trig_cum)

        fom_ks = KolgomorovSmirnov()
        for channel in self.available_channels:
            h_aux = h_aux_cum[channel]
            h_trig = h_trig_cum[channel]
            h_aux.align(h_trig)

            fom_ks.calculate(channel, h_aux=h_aux, h_trig=h_trig)

        for k, v in sorted(fom_ks.scores.items(), key=lambda f: f[1], reverse=True):
            print(k, v)

        # h = Hist(segment_50hz.x)
        # plt.bar(h.xgrid, h.counts, width=h.span / h.nbin)
        # plt.xlim([h.offset, h.offset + h.span])
        # plt.show()

    def decimate_data(self, f_target=50):
        decimator = Decimator(f_target=f_target)

        aux_data = FFLCache(ffl_file=self.source, f_target=None, gps_start=self.t_start, gps_end=self.t_stop)
        segments = aux_data.segments

        for segment in tqdm(segments):
            gps_start, gps_end = segment
            ds_data = np.zeros((self.n_channels, int((gps_end - gps_start) * f_target)))
            for i, channel in enumerate(self.available_channels):
                channel_segment = self.reader.get_channel(channel_name=channel,
                                                          t_start=gps_start,
                                                          t_stop=gps_end,
                                                          source=self.source)
                ds_segment = decimator.decimate(segment=channel_segment)
                ds_data[i, :] = ds_segment.data
            file_path = self.ds_data_path + self.FILE_TEMPLATE.format(f_target=self.f_target,
                                                                      t_start=gps_start,
                                                                      t_stop=gps_end)
            np.save(file_path, ds_data)

    def construct_histograms(self, channels, aux_data, segments, triggers) -> ({str, Hist}):
        h_aux_cum = dict((c, Hist([])) for c in channels)
        h_trig_cum = dict((c, Hist([])) for c in channels)

        cum_aux_veto = [np.zeros(int(round(abs(segment) * self.f_target)), dtype=bool) for segment in segments]
        cum_trig_veto = [np.zeros(count_triggers_in_segment(triggers, *segment), dtype=bool) for segment in segments]

        LOG.info('Constructing histograms...')
        for i, segment, gap in iter_segments(segments):
            gps_start, gps_end = segment
            if gap:
                pass  # todo: when transformations are implemented -> reset

            if count_triggers_in_segment(triggers, gps_start, gps_end) == 0:
                continue
            seg_triggers = triggers[slice_triggers_in_segment(triggers, gps_start, gps_end)]
            i_trigger = np.floor((seg_triggers - gps_start) * self.f_target).astype(np.int32)

            for channel in tqdm(channels, position=0, leave=True):
                x_aux = aux_data.get_data_from_segment(request_segment=segment, channel=channel)
                x_trig = x_aux[i_trigger]
                # todo: handle non-finite values. Either discard channel or replace values.

                # todo: apply transformations to the data
                # for transform in transformations do ...
                x_aux_veto = x_aux[~cum_aux_veto[i]]
                x_trig_veto = x_trig[~cum_trig_veto[i]]

                h_aux = Hist(x_aux_veto, spanlike=h_aux_cum[channel])
                h_trig = Hist(x_trig_veto, spanlike=h_aux)
                h_aux_cum[channel] += h_aux
                h_trig_cum[channel] += h_trig

        return h_aux_cum, h_trig_cum


if __name__ == '__main__':
    excavator = Excavator(source='/virgoData/ffl/raw_O3b_arch',
                          channel_name='V1:Hrec_hoft_2_200Hz',
                          t_start=1262230000,
                          t_stop=1262240000)
    # excavator.run(n_iter=1)
    excavator.decimate_data()
