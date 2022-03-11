from tqdm import tqdm
import sys

from application1.utils import *
from application1.model.histogram import Hist
from application1.model.ffl_cache import FFLCache
from application1.model.fom import KolgomorovSmirnov
from application1.handler.data.reader.frame_file import FrameFileReader
from application1.handler.data.reader.h5 import H5Reader
from application1.handler.data.writer import DataWriter
from application1.handler.data.resampler import Resampler
from application1.handler.triggers import DefaultPipeline
from application1.config import ConfigurationManager

LOG = ConfigurationManager.get_logger(__name__)


class Excavator:
    EXCLUDE_PATTERNS = ['*max', '*min', 'V1:VAC*', 'V1:Daq*', '*rms']

    def __init__(self, source, channel_name, t_start, t_stop, f_target=50, channel_bl_patterns=None):
        self.source = source
        self.channel_name = channel_name
        self.t_start = t_start
        self.t_stop = t_stop
        self.f_target = f_target

        bl_patterns = channel_bl_patterns if channel_bl_patterns else self.EXCLUDE_PATTERNS
        self.h5_reader = H5Reader(gps_start=t_start, gps_end=t_stop)
        self.ff_reader = FrameFileReader(source)
        self.ff_reader.set_patterns(patterns=bl_patterns)
        self.writer = DataWriter()

        self.available_channels = self.h5_reader.get_available_channels()
        LOG.info(f'Found {len(self.available_channels)} available channels.')

    def run(self, n_iter=1):

        # trigger_pipeline = Omicron(channel=available_channels[0])
        trigger_pipeline = DefaultPipeline(trigger_file='GSpy_ALLIFO_O3b_0921_final', trigger_type="Scattered_Light")
        triggers = trigger_pipeline.get_segment(gps_start=self.t_start, gps_end=self.t_stop)
        if triggers.size == 0:
            LOG.error(f"No triggers found between {self.t_start} and {self.t_stop}, aborting...")
            sys.exit(1)

        h_aux_cum, h_trig_cum = self.construct_histograms(segments=self.h5_reader.segments,
                                                          triggers=triggers)

        fom_ks = KolgomorovSmirnov()
        for channel in self.available_channels:
            h_aux = h_aux_cum[channel]
            h_trig = h_trig_cum[channel]
            h_aux.align(h_trig)

            fom_ks.calculate(channel, h_aux=h_aux, h_trig=h_trig)

        for k, v in sorted(fom_ks.scores.items(), key=lambda f: f[1], reverse=True)[0:10]:
            print(k, v)

        # h = Hist(segment_50hz.x)
        # plt.bar(h.xgrid, h.counts, width=h.span / h.nbin)
        # plt.xlim([h.offset, h.offset + h.span])
        # plt.show()

    def decimate_data(self):
        decimator = Resampler(f_target=self.f_target, method='mean')
        aux_data = FFLCache(ffl_file=self.source, gps_start=self.t_start, gps_end=self.t_stop)
        decimator.downsample_ffl(ffl_cache=aux_data)

    def construct_histograms(self, segments, triggers) -> ({str, Hist}):
        h_aux_cum = dict((c, Hist([])) for c in self.available_channels)
        h_trig_cum = dict((c, Hist([])) for c in self.available_channels)

        cum_aux_veto = [np.zeros(int(round(abs(segment) * self.f_target)), dtype=bool) for segment in segments]
        cum_trig_veto = [np.zeros(count_triggers_in_segment(triggers, *segment), dtype=bool) for segment in segments]

        LOG.info('Constructing histograms...')
        for i, segment, gap in iter_segments(segments):
            gps_start, gps_end = segment
            if gap:
                pass  # todo: when transformations are implemented -> reset

            if count_triggers_in_segment(triggers, gps_start, gps_end) == 0:
                LOG.info(f'No triggers found from {gps_start} to {gps_end}')
                continue
            seg_triggers = triggers[slice_triggers_in_segment(triggers, gps_start, gps_end)]
            i_trigger = np.floor((seg_triggers - gps_start) * self.f_target).astype(np.int32)

            for channel in tqdm(self.available_channels, position=0, leave=True):
                x_aux = self.h5_reader.get_data_from_segments(request_segment=segment, channel_name=channel)
                if x_aux is None:
                    self.available_channels.remove(channel)
                    continue
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
            self.h5_reader.reset_cache()

        return h_aux_cum, h_trig_cum


if __name__ == '__main__':
    excavator = Excavator(source='/virgoData/ffl/raw_O3b_arch',
                          channel_name='V1:Hrec_hoft_2_200Hz',
                          t_start=1263323000,
                          t_stop=1263324000)
    excavator.run()
    # excavator.decimate_data()
