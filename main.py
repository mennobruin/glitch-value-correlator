import os
import pickle
import sys

import numpy as np
from tqdm import tqdm

from application1.config import config_manager
from application1.handler.data.reader.ffl import FrameFileReader
from application1.handler.data.reader.h5 import H5Reader
from application1.handler.data.resampler import Resampler
from application1.handler.data.writer import DataWriter
from application1.handler.triggers import DefaultPipeline, Omicron
from application1.model.ffl_cache import FFLCache
from application1.model.fom import KolgomorovSmirnov, AndersonDarling
from application1.model.histogram import Hist
from application1.model.transformation import do_transformations, GaussianDifferentiator, \
    SavitzkyGolayDifferentiator, HighPass, Abs
from application1.plotting.plot import plot_histogram_cdf
from application1.plotting.report import HTMLReport
from application1.utils import count_triggers_in_segment, slice_triggers_in_segment, iter_segments
from resources.constants import CONFIG_FILE, RESOURCE_DIR

LOG = config_manager.get_logger(__name__)

"""
 - done: implement transformations
 - blocked: implement parallel processing for histograms
 - done: think about potential new transformations
 - done: create argument parser + default values file which remembers previous inputs
"""


class Excavator:

    def __init__(self):
        LOG.info(f"Loading configuration from {CONFIG_FILE}.")
        self.config = config_manager.load_config()
        self.source = self.config['project.source']
        self.t_start = self.config['project.start_time']
        self.t_stop = self.config['project.end_time']
        self.f_cutoff = self.config['project.cutoff_frequency']
        self.f_target = self.config['project.target_frequency']
        with open(self.config['project.blacklist_patterns'], 'r') as f:
            bl_patterns: list = f.read().splitlines()

        if self.config['project.decimate']:
            self.reader = H5Reader(gps_start=self.t_start,
                                   gps_end=self.t_stop,
                                   exclude_patterns=bl_patterns)
        else:
            self.reader = FrameFileReader(source=self.source,
                                          gps_start=self.t_start,
                                          gps_end=self.t_stop,
                                          exclude_patterns=bl_patterns)
        self.n_points = int(round(abs(self.reader.segments[0]) * self.f_target))
        self.writer = DataWriter()
        self.report = HTMLReport()
        self.histogram_file = RESOURCE_DIR + 'histograms.pickle'

        self.available_channels = None
        self.labels = None
        self.cum_aux_veto = None
        self.cum_trig_veto = None
        self.transformation_names = None
        self.transformation_states = None
        self.transformation_combinations = None
        self.h_aux_cum = None
        self.h_trig_cum = None
        self.i_trigger = None

    def run(self, n_iter=1, load_existing=False):

        self.available_channels = self.reader.get_available_channels()
        self.available_channels = list(np.random.choice(self.available_channels, size=5000))
        LOG.info(f'Found {len(self.available_channels)} available channels.')

        # trigger_pipeline = Omicron(channel=self.available_channels[0])
        trigger_pipeline = DefaultPipeline(
            trigger_file='GSpy_ALLIFO_O3b_0921_final')  # , trigger_type="Scattered_Light")
        self.labels = trigger_pipeline.labels
        triggers = trigger_pipeline.get_segment(gps_start=self.t_start, gps_end=self.t_stop)
        if triggers.size == 0:
            LOG.error(f"No triggers found between {self.t_start} and {self.t_stop}, aborting...")
            sys.exit(1)

        self.init_transformations()

        test_file = f'test_{self.t_start}_{self.t_stop}.pickle'
        if load_existing and os.path.exists(test_file):
            with open(test_file, 'rb') as pkf:
                data = pickle.load(pkf)
                self.h_trig_cum = data['trig']
                print(len(self.h_trig_cum.values()))
                print(self.h_trig_cum.keys())
                self.h_aux_cum = data['aux']
                self.available_channels = data['channels']
        else:
            self.construct_histograms(segments=self.reader.segments, triggers=triggers)
            with open(test_file, 'wb') as pkf:
                pickle.dump({'trig': self.h_trig_cum, 'aux': self.h_aux_cum, 'channels': self.available_channels}, pkf)

        fom_ks = KolgomorovSmirnov()
        fom_ad = AndersonDarling()
        for channel in self.available_channels:
            for transformation_name in self.transformation_names:
                h_aux = self.h_aux_cum[channel, transformation_name]
                h_trig = Hist(np.array([]))
                for label in self.h_trig_cum:
                    h_trig += self.h_trig_cum[channel, transformation_name, label]
                try:
                    h_aux.align(h_trig)

                    fom_ks.calculate(channel, transformation_name, h_aux, h_trig)
                    fom_ad.calculate(channel, transformation_name, h_aux, h_trig)
                except AssertionError:
                    print(channel, transformation_name)
                    print(h_aux)
                    print(h_trig)
                    print('-------------------------')

        ks_table_cols = ['Channel', 'Transformation', 'KS', 'p-value']
        ks_table = 'KS_table'
        self.report.add_tag(tag_type='table', tag_id=ks_table)
        self.report.add_row_to_table(content=ks_table_cols, tag='th', table_id=ks_table)

        ad_table_cols = ['Channel', 'Transformation', 'AD', f'below alpha={fom_ad.critical_value}']
        ad_table = 'AD_table'
        self.report.add_tag(tag_type='table', tag_id=ad_table)
        self.report.add_row_to_table(content=ad_table_cols, tag='th', table_id=ad_table)

        ks_results = sorted(fom_ks.scores.items(), key=lambda f: f[1].d_n, reverse=True)
        ad_results = sorted(fom_ad.scores.items(), key=lambda f: f[1].ad, reverse=True)
        self.writer.write_csv(ks_results, 'ks_results.csv', file_path=self.writer.default_path + 'results/')
        self.writer.write_csv(ad_results, 'ad_results.csv', file_path=self.writer.default_path + 'results/')

        images_div = 'images'
        self.report.add_tag(tag_type='div', tag_id=images_div)
        for i, (k, v) in enumerate(ks_results[0:10]):
            channel, transformation = k
            statistic, p_value = v
            try:
                div_id = f'rank_{i}'
                self.report.add_tag(tag_type='div', tag_id=div_id, parent_div=images_div)
                cdf_fig = plot_histogram_cdf(histogram=self.h_aux_cum[channel, transformation],
                                             channel=channel,
                                             transformation=transformation,
                                             data_type='aux',
                                             return_fig=True,
                                             rank=i)
                cdf_fname = plot_histogram_cdf(histogram=self.h_trig_cum[channel, transformation],
                                               channel=channel,
                                               transformation=transformation,
                                               data_type='trig',
                                               fig=cdf_fig,
                                               save=True,
                                               rank=i)
                self.report.add_image(img=cdf_fname, div_id=div_id)
            except AttributeError as e:
                LOG.debug(e)
            self.report.add_row_to_table(content=[channel, transformation, round(statistic, 3), f'{p_value:.2E}'],
                                         table_id=ks_table)

        for i, (k, v) in enumerate(ad_results[0:10]):
            channel, transformation = k
            statistic, threshold = v
            self.report.add_row_to_table(content=[channel, transformation, round(statistic, 3), str(threshold)],
                                         table_id=ad_table)

    def generate_report(self):
        LOG.info("Generating HTML Report...")
        print(self.report)
        self.report.run_html()

    def decimate_data(self):
        decimator = Resampler(f_target=self.f_target, method='mean')
        aux_data = FFLCache(ffl_file=self.source, gps_start=self.t_start, gps_end=self.t_stop)
        decimator.downsample_ffl(ffl_cache=aux_data)

    def init_transformations(self):
        window_length = self.n_points / 2 if self.n_points / 2 % 2 == 1 else self.n_points / 2 + 1  # must be odd
        savitzky_golay = SavitzkyGolayDifferentiator(window_length=window_length, dx=1 / self.n_points)
        gauss = GaussianDifferentiator(n_points=self.n_points)

        self.transformation_combinations = [
            [],  # also do a run untransformed
            # [savitzky_golay],
            # [savitzky_golay, AbsMean],
            # [gauss],
            # [gauss, Abs],
            [Abs]
            # [AbsMean],
            # [HighPass]
        ]

        join_names = lambda c: '_'.join(t.NAME for t in c)
        self.transformation_names = [join_names(t) for t in self.transformation_combinations]
        self.transformation_states = {
            channel: {self.transformation_names[i]: t for i, t in enumerate(self.transformation_combinations)}
            for channel in self.available_channels}

        for channel in self.available_channels:
            for name, transformations in self.transformation_states[channel].items():
                for i, transformation in enumerate(transformations):
                    if isinstance(transformation, type):
                        self.transformation_states[channel][name][i] = transformation(f_target=self.f_cutoff)

    def _init_cumulative_hists(self, segments, triggers):
        self.cum_aux_veto = [np.zeros(self.n_points, dtype=bool) for _ in segments]
        self.cum_trig_veto = {
            label: [np.zeros(count_triggers_in_segment(triggers[triggers.label == label], *segment), dtype=bool)
                    for segment in segments]
            for label in self.labels
        }

        self.h_aux_cum = {
            (channel, transform): Hist(np.array([]))
            for channel in self.available_channels for transform in self.transformation_names
        }
        self.h_trig_cum = {
            (channel, transform, label): Hist(np.array([]))
            for channel in self.available_channels
            for transform in self.transformation_names
            for label in self.labels
        }

    def construct_histograms(self, segments, triggers) -> ({str, Hist}):
        self._init_cumulative_hists(segments, triggers)

        LOG.info('Constructing histograms...')
        for i_segment, segment, gap in iter_segments(segments):
            gps_start, gps_end = segment
            if gap:
                for combination in self.transformation_combinations:
                    for transformation in combination:
                        transformation.reset()

            if count_triggers_in_segment(triggers, gps_start, gps_end) == 0:
                LOG.info(f'No triggers found from {gps_start} to {gps_end}')
                continue
            seg_triggers = triggers[slice_triggers_in_segment(triggers, gps_start, gps_end)]
            self.i_trigger = {}
            for label in self.labels:
                label_triggers = seg_triggers[seg_triggers.label == label]
                self.i_trigger[label] = np.floor((label_triggers.GPStime - gps_start) * self.f_target).astype(np.int32)
            for channel in tqdm(self.available_channels, position=0, leave=True, desc=f'{segment[0]} -> {segment[1]}'):
                self.update_channel_histogram(i_segment, segment, channel)
            self.reader._reset_cache()

    def _discard_channel(self, channel):
        self.available_channels.remove(channel)
        for transform in self.transformation_names:
            del self.h_aux_cum[channel, transform]
            for label in self.labels:
                del self.h_trig_cum[channel, transform, label]

    def update_channel_histogram(self, i, segment, channel):
        try:
            x_aux = self.reader.get_data_from_segments(request_segment=segment, channel_name=channel)
        except UnicodeDecodeError:
            self._discard_channel(channel)
            LOG.debug(f'Discarded {channel} due to decoding error.')
            return
        if x_aux is None:
            self._discard_channel(channel)
            LOG.debug(f'Discarded {channel} due to disappearance.')
            return
        for transformation_name in self.transformation_names:
            x_transform = do_transformations(
                transformations=self.transformation_states[channel][transformation_name],
                data=x_aux)
            try:
                aux_hist = self.get_histogram(data=x_transform,
                                              cumulative_veto=self.cum_aux_veto[i],
                                              spanlike=self.h_aux_cum[channel, transformation_name])
                self.h_aux_cum[channel, transformation_name] += aux_hist

                for label, i_trigger in self.i_trigger.items():
                    trig_hist = self.get_histogram(data=x_transform[i_trigger],
                                                   cumulative_veto=self.cum_trig_veto[label][i],
                                                   spanlike=aux_hist)
                    self.h_trig_cum[channel, transformation_name, label] += trig_hist
            except (OverflowError, AssertionError, IndexError) as e:
                LOG.debug(f'Exception caught for channel {channel}: {e}, discarding.')
                self._discard_channel(channel)
                return
            except KeyError:
                self.available_channels.remove(channel)
                return

    @staticmethod
    def get_histogram(data, cumulative_veto, spanlike):
        x_veto = data[~cumulative_veto]
        return Hist(x_veto, spanlike=spanlike)


if __name__ == '__main__':
    LOG.info("-+-+-+-+-+- RUN START -+-+-+-+-+-")
    excavator = Excavator()
    excavator.run(load_existing=False)
    excavator.generate_report()
    # excavator.decimate_data()
    LOG.info("-+-+-+-+-+- RUN END -+-+-+-+-+-")
