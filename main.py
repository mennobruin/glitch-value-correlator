from tqdm import tqdm
import sys

from application1.utils import *
from application1.model.histogram import Hist
from application1.model.ffl_cache import FFLCache
from application1.model.fom import KolgomorovSmirnov
from application1.model.transformation import *
from application1.handler.data.reader.frame_file import FrameFileReader
from application1.handler.data.reader.h5 import H5Reader
from application1.handler.data.writer import DataWriter
from application1.handler.data.resampler import Resampler
from application1.handler.triggers import DefaultPipeline
from application1.config import config_manager

LOG = config_manager.get_logger(__name__)

"""
 - done: implement transformations
 - todo: implement parallel processing for histograms
 - done: think about potential new transformations
 - todo: create argument parser + default values file which remembers previous inputs
"""


class Excavator:
    EXCLUDE_PATTERNS = ['*max', '*min', 'V1:VAC*', 'V1:Daq*', '*rms', '*_DS', '*_notsafe']

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
        n_points = int(round(abs(segments[0]) * self.f_target))
        cum_aux_veto = [np.zeros(n_points, dtype=bool) for _ in segments]
        cum_trig_veto = [np.zeros(count_triggers_in_segment(triggers, *segment), dtype=bool) for segment in segments]

        savitzky_golay = SavitzkyGolayDifferentiator(window_length=n_points / 2, dx=1 / n_points)
        gauss = GaussianDifferentiator(n_points=n_points)

        transformation_combinations = [
            [],  # also do a run untransformed
            [savitzky_golay],
            [savitzky_golay, AbsMean],
            [gauss],
            [gauss, AbsMean],
            [AbsMean],
            [HighPass]
        ]

        join_names = lambda c: '_'.join(t.NAME for t in c)
        transformation_names = [join_names(t) for t in transformation_combinations]
        transformation_states = {channel: {transformation_names[i]: t for i, t in enumerate(transformation_combinations)}
                                 for channel in self.available_channels}

        for channel in self.available_channels:
            for name, transformations in transformation_states[channel].items():
                for i, transformation in enumerate(transformations):
                    if isinstance(transformation, type):
                        transformation_states[channel][name][i] = transformation(f_target=self.f_target)

        h_aux_cum = dict(((c, t), Hist([])) for c in self.available_channels for t in transformation_names)
        h_trig_cum = dict(((c, t), Hist([])) for c in self.available_channels for t in transformation_names)

        LOG.info('Constructing histograms...')
        for i, segment, gap in iter_segments(segments):
            gps_start, gps_end = segment
            if gap:
                for combination in transformation_combinations:
                    for transformation in combination:
                        transformation.reset()

            if count_triggers_in_segment(triggers, gps_start, gps_end) == 0:
                LOG.info(f'No triggers found from {gps_start} to {gps_end}')
                continue
            seg_triggers = triggers[slice_triggers_in_segment(triggers, gps_start, gps_end)]
            i_trigger = np.floor((seg_triggers - gps_start) * self.f_target).astype(np.int32)

            for channel in tqdm(self.available_channels, position=0, leave=True):
                x_aux = self.h5_reader.get_data_from_segments(request_segment=segment, channel_name=channel)
                if x_aux is None:
                    self.available_channels.remove(channel)
                    LOG.debug(f'Discarded {channel} due to disappearance.')
                    continue
                for transformation_name in transformation_names:
                    x_transform = do_transformations(transformations=transformation_states[channel][transformation_name],
                                                     data=x_aux)
                    aux_hist = self.update_histogram(data=x_transform,
                                                     cumulative_veto=cum_aux_veto[i],
                                                     spanlike=h_aux_cum[channel])
                    trig_hist = self.update_histogram(data=x_transform[i_trigger],
                                                      cumulative_veto=cum_trig_veto[i],
                                                      spanlike=aux_hist)
                    h_aux_cum[channel, transformation_name] += aux_hist
                    h_trig_cum[channel, transformation_name] += trig_hist

            self.h5_reader.reset_cache()

        return h_aux_cum, h_trig_cum

    @staticmethod
    def update_histogram(data, cumulative_veto, spanlike):
        x_veto = data[~cumulative_veto]
        return Hist(x_veto, spanlike=spanlike)


if __name__ == '__main__':
    LOG.info("-+-+-+-+-+- RUN START -+-+-+-+-+-")
    excavator = Excavator(source='/virgoData/ffl/raw_O3b_arch',
                          channel_name='V1:Hrec_hoft_2_200Hz',
                          t_start=1263323000,
                          t_stop=1263324000)
    excavator.run()
    # excavator.decimate_data()
    LOG.info("-+-+-+-+-+- RUN END -+-+-+-+-+-")
