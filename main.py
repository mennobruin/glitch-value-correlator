from tqdm import tqdm
import sys
import bs4

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
from application1.plotting.plot import *
from application1.plotting.report import HTMLReport
from resources.constants import *

LOG = config_manager.get_logger(__name__)

"""
 - done: implement transformations
 - todo: implement parallel processing for histograms
 - done: think about potential new transformations
 - todo: create argument parser + default values file which remembers previous inputs
"""


class Excavator:

    def __init__(self):
        self.config = config_manager.load_config()
        self.source = self.config['project.source']
        self.t_start = self.config['project.start_time']
        self.t_stop = self.config['project.end_time']
        self.f_target = self.config['project.target_frequency']
        with open(self.config['project.blacklist_patterns'], 'r') as f:
            bl_patterns: list = f.readlines()

        self.h5_reader = H5Reader(gps_start=self.t_start, gps_end=self.t_stop)
        self.ff_reader = FrameFileReader(self.source)
        self.ff_reader.set_patterns(patterns=bl_patterns)
        self.writer = DataWriter()
        self.report = HTMLReport()

        self.available_channels = self.h5_reader.get_available_channels()
        LOG.info(f'Found {len(self.available_channels)} available channels.')

        self.cum_aux_veto = None
        self.cum_trig_veto = None
        self.transformation_names = None
        self.transformation_states = None
        self.h_aux_cum = None
        self.h_trig_cum = None
        self.i_trigger = None

    def run(self, n_iter=1):

        # trigger_pipeline = Omicron(channel=available_channels[0])
        trigger_pipeline = DefaultPipeline(trigger_file='GSpy_ALLIFO_O3b_0921_final', trigger_type="Scattered_Light")
        triggers = trigger_pipeline.get_segment(gps_start=self.t_start, gps_end=self.t_stop)
        if triggers.size == 0:
            LOG.error(f"No triggers found between {self.t_start} and {self.t_stop}, aborting...")
            sys.exit(1)

        self.construct_histograms(segments=self.h5_reader.segments, triggers=triggers)

        fom_ks = KolgomorovSmirnov()
        for channel in self.available_channels:
            for transformation_name in self.transformation_names:
                h_aux = self.h_aux_cum[channel, transformation_name]
                h_trig = self.h_trig_cum[channel, transformation_name]
                h_aux.align(h_trig)

                fom_ks.calculate(channel, transformation_name, h_aux, h_trig)

        self.report.add_row_to_table(content=['Channel', 'Transformation', 'KS Statistic'], tag='th', table_class='KS')

        for i, (k, v) in enumerate(sorted(fom_ks.scores.items(), key=lambda f: f[1], reverse=True)[0:3]):
            print(k, v)
            channel, transformation = k
            fig = plot_histogram_cdf(histogram=self.h_aux_cum[channel, transformation],
                                     channel=channel,
                                     transformation=transformation,
                                     data_type='aux',
                                     return_fig=True,
                                     score=i)
            fname = plot_histogram_cdf(histogram=self.h_trig_cum[channel, transformation],
                                       channel=channel,
                                       transformation=transformation,
                                       data_type='trig',
                                       fig=fig,
                                       save=True,
                                       score=i)
            self.report.add_row_to_table(content=[channel, transformation, v], table_class='KS')
            self.report.add_image(img=fname, div_class='images')

    def generate_report(self):
        LOG.info("Generating HTML Report...")
        self.report.run_html()

    def decimate_data(self):
        decimator = Resampler(f_target=self.f_target, method='mean')
        aux_data = FFLCache(ffl_file=self.source, gps_start=self.t_start, gps_end=self.t_stop)
        decimator.downsample_ffl(ffl_cache=aux_data)

    def construct_histograms(self, segments, triggers) -> ({str, Hist}):
        n_points = int(round(abs(segments[0]) * self.f_target))
        self.cum_aux_veto = [np.zeros(n_points, dtype=bool) for _ in segments]
        self.cum_trig_veto = [np.zeros(count_triggers_in_segment(triggers, *segment), dtype=bool) for segment in segments]

        window_length = n_points / 2 if n_points / 2 % 2 == 1 else n_points / 2 + 1  # must be odd
        savitzky_golay = SavitzkyGolayDifferentiator(window_length=window_length, dx=1 / n_points)
        gauss = GaussianDifferentiator(n_points=n_points)

        transformation_combinations = [
            [],  # also do a run untransformed
            # [savitzky_golay],
            # [savitzky_golay, AbsMean],
            [gauss],
            # [gauss, Abs],
            # [AbsMean],
            [HighPass]
        ]

        join_names = lambda c: '_'.join(t.NAME for t in c)
        self.transformation_names = [join_names(t) for t in transformation_combinations]
        self.transformation_states = {
            channel: {self.transformation_names[i]: t for i, t in enumerate(transformation_combinations)}
            for channel in self.available_channels}

        for channel in self.available_channels:
            for name, transformations in self.transformation_states[channel].items():
                for i, transformation in enumerate(transformations):
                    if isinstance(transformation, type):
                        self.transformation_states[channel][name][i] = transformation(f_target=self.f_target)

        self.h_aux_cum = dict(((c, t), Hist([])) for c in self.available_channels for t in self.transformation_names)
        self.h_trig_cum = dict(((c, t), Hist([])) for c in self.available_channels for t in self.transformation_names)

        LOG.info('Constructing histograms...')
        for i_segment, segment, gap in iter_segments(segments):
            gps_start, gps_end = segment
            if gap:
                for combination in transformation_combinations:
                    for transformation in combination:
                        transformation.reset()

            if count_triggers_in_segment(triggers, gps_start, gps_end) == 0:
                LOG.info(f'No triggers found from {gps_start} to {gps_end}')
                continue
            seg_triggers = triggers[slice_triggers_in_segment(triggers, gps_start, gps_end)]
            self.i_trigger = np.floor((seg_triggers - gps_start) * self.f_target).astype(np.int32)
            for channel in tqdm(self.available_channels, position=0, leave=True):
                self.update_channel_histogram(i_segment, segment, channel)
            self.h5_reader.reset_cache()

    def update_channel_histogram(self, i, segment, channel):
        x_aux = self.h5_reader.get_data_from_segments(request_segment=segment, channel_name=channel)
        if x_aux is None:
            self.available_channels.remove(channel)
            LOG.debug(f'Discarded {channel} due to disappearance.')
            return
        for transformation_name in self.transformation_names:
            x_transform = do_transformations(
                transformations=self.transformation_states[channel][transformation_name],
                data=x_aux)
            aux_hist = self.get_histogram(data=x_transform,
                                          cumulative_veto=self.cum_aux_veto[i],
                                          spanlike=self.h_aux_cum[channel, transformation_name])
            trig_hist = self.get_histogram(data=x_transform[self.i_trigger],
                                           cumulative_veto=self.cum_trig_veto[i],
                                           spanlike=aux_hist)
            try:
                self.h_aux_cum[channel, transformation_name] += aux_hist
                self.h_trig_cum[channel, transformation_name] += trig_hist
            except OverflowError as e:
                LOG.debug(f'OverflowError for channel {channel}: {e}, discarding.')
                self.available_channels.remove(channel)
                return

    @staticmethod
    def get_histogram(data, cumulative_veto, spanlike):
        x_veto = data[~cumulative_veto]
        return Hist(x_veto, spanlike=spanlike)


if __name__ == '__main__':
    LOG.info("-+-+-+-+-+- RUN START -+-+-+-+-+-")
    excavator = Excavator(source='/virgoData/ffl/raw_O3b_arch',
                          channel_name='V1:Hrec_hoft_2_200Hz',
                          t_start=1263323000,
                          t_stop=1263323100)
    excavator.run()
    excavator.generate_report()
    # excavator.decimate_data()
    LOG.info("-+-+-+-+-+- RUN END -+-+-+-+-+-")
