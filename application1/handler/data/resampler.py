import numpy as np
import os
import h5py
import math
import multiprocessing as mp
import scipy.signal as sig
import warnings

from tqdm import tqdm

from resources.constants import RESOURCE_DIR
from application1.model.ffl_cache import FFLCache
from application1.config import config_manager
from application1.utils.tools import almost_int

from virgotools.frame_lib import FrameFile, FrVect2array

LOG = config_manager.get_logger(__name__)


class Resampler:

    FILE_TEMPLATE = 'excavator_f{f_target}_gs{t_start}_ge{t_stop}_{method}'
    FILTER_ORDER = 4
    MAX_DS_RATIO = 10
    FRAME_DURATION = 10
    FRAMES_IN_FRAME_FILE = 10

    def __init__(self, f_target, method='mean'):
        self.f_target = f_target
        self.n_target = f_target * self.FRAME_DURATION
        self.method = method
        self.ds_path = RESOURCE_DIR + 'ds_data/'
        self.ds_data_path = self.ds_path + 'data/'
        os.makedirs(self.ds_data_path, exist_ok=True)
        LOG.info(f'Storing downsampled data at {self.ds_data_path}')
        self.source = None
        self.filt_cache = {}
        self.ignored_channels = set()

    def downsample_ffl(self, ffl_cache: FFLCache):
        segments = [(gs, ge) for (gs, ge) in ffl_cache.segments]
        self.source = ffl_cache.ffl_file

        n_cpu = min(mp.cpu_count() - 1, len(segments))
        with mp.get_context('spawn').Pool(n_cpu) as pool:
            for _ in tqdm(pool.imap_unordered(self.process_segment, segments), total=len(segments)):
                pass
        print(f'number of ignored channels: {len(self.ignored_channels)}')

    def process_segment(self, segment):
        gps_start, gps_end = segment

        file_name = self.FILE_TEMPLATE.format(f_target=self.f_target,
                                              t_start=int(gps_start),
                                              t_stop=int(gps_end),
                                              method=self.method)
        file_path = self.ds_data_path + file_name
        # if os.path.exists(file_path):
        #     LOG.info(f'Found existing data from {gps_start} to {gps_end} at {file_name}, skipping...')
        #     return
        with h5py.File(file_path + '.h5', 'w') as h5f:
            for t in np.arange(gps_start, gps_end, self.FRAME_DURATION):
                self._store_data(h5_file=h5f, t=t, gps_start=gps_start)

    def _store_data(self, h5_file, t, gps_start):
        with FrameFile(self.source).get_frame(t) as ff:
            for adc in ff.iter_adc():
                f_sample = adc.contents.sampleRate
                if f_sample >= 50:
                    channel = str(adc.contents.name)
                    if channel in self.ignored_channels:
                        continue
                    ds_adc = self.downsample_adc(adc, f_sample)
                    if ds_adc is None:
                        self.ignored_channels.add(channel)
                        continue
                    if t == gps_start:
                        ds_data = np.zeros(self.n_target * self.FRAMES_IN_FRAME_FILE)
                        ds_data[0:self.n_target] = ds_adc
                        h5_file.create_dataset(name=channel, data=ds_data)
                    else:
                        i = int((t - gps_start) * self.f_target)
                        j = i + self.n_target
                        h5_file[channel][i:j] = ds_adc

    def downsample_adc(self, adc, f_sample):
        data = FrVect2array(adc.contents.data)
        if data.size < self.n_target:
            return None
        ds_data = None

        if self.method == 'mean':
            try:
                ds_data = self._resample_mean(data)
            except ValueError as e:
                print(adc.contents.name)
                print(adc.contents.sampleRate)
                print(data.size)
                raise e
        elif self.method == 'filt':
            ds_data = self._decimate(data, f_sample).astype(np.float64)
        elif self.method == 'filtfilt':
            ds_data = self._decimate(data, f_sample, filtfilt=True).astype(np.float64)
        else:
            LOG.error(f"No implementation found for resampling method '{self.method}'.")

        return ds_data

    def _resample_mean(self, data):
        n_points = data.size
        ds_ratio = n_points / self.n_target
        if math.isclose(ds_ratio, 1):  # f_sample ~= f_target
            return data

        pad = False
        if not almost_int(ds_ratio):
            n_padding = round(np.ceil(n_points / self.n_target) * self.n_target) - n_points
            data = self._add_padding(data, n_padding)
            n_points = data.size
            ds_ratio = n_points / self.n_target
            pad = True

        data = self._n_sample_average(data, ratio=round(ds_ratio))
        if pad:
            for row in data.reshape(25, 200):
                print(row)
            raise ValueError
        return data

    @staticmethod
    def _add_padding(data, n_padding):
        padding = np.empty(n_padding)
        padding.fill(np.nan)
        data = np.append(data, padding)
        return data

    @staticmethod
    def _n_sample_average(x: np.array, ratio: int):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            return np.nanmean(x.reshape(-1, ratio), axis=1)

    def _decimate(self, data, f_sample, filtfilt=False):
        ds_ratio = f_sample / self.f_target

        if math.isclose(ds_ratio, 1):  # f_sample ~= f_target
            return data

        if ds_ratio.is_integer():  # decimate
            ratios = self._split_downsample_ratio(ds_ratio)
            for ds_ratio in ratios:
                if ds_ratio not in self.filt_cache:
                    self.filt_cache[ds_ratio] = sig.cheby1(N=self.FILTER_ORDER, rp=0.05, Wn=0.8 / ds_ratio, output='sos')
                if filtfilt:
                    data = sig.sosfiltfilt(self.filt_cache[ds_ratio], data)[::int(ds_ratio)]
                else:
                    data = sig.sosfilt(self.filt_cache[ds_ratio], data)[::int(ds_ratio)]
            return data
        else:
            return self._resample(data)

    def _split_downsample_ratio(self, ds_ratio) -> [int]:
        if ds_ratio > self.MAX_DS_RATIO:
            ds_ratio_log10 = np.log10(ds_ratio)
            factor, remainder = int(ds_ratio_log10), round(np.power(10, ds_ratio_log10 % 1))
            if remainder != 0:
                return [self.MAX_DS_RATIO] * factor + [remainder]
            else:
                return [self.MAX_DS_RATIO] * factor
        else:
            return [ds_ratio]

    def _resample(self, data):  # Fourier resampling
        return sig.resample(data, self.n_target, window='hamming')
