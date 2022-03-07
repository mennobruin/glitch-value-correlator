import numpy as np
import os
import h5py
import math
import multiprocessing as mp
import scipy.signal as sig

from tqdm import tqdm

from core.config.configuration_manager import ConfigurationManager
from application1.utils import get_resource_path
from application1.model.ffl_cache import FFLCache
from application1.handler.data.reader.reader import BaseReader

from virgotools.frame_lib import FrameFile, FrVect2array

LOG = ConfigurationManager.get_logger(__name__)


class Resampler:

    FILE_TEMPLATE = 'excavator_f{f_target}_gs{t_start}_ge{t_stop}_{method}'
    FILTER_ORDER = 4
    FRAME_DURATION = 10
    FRAMES_IN_FRAME_FILE = 10

    def __init__(self, f_target, reader: BaseReader, method='mean'):
        self.f_target = f_target
        self.n_target = f_target * self.FRAME_DURATION
        self.method = method
        self.resource_path = get_resource_path(depth=1)
        self.ds_path = self.resource_path + 'ds_data/'
        self.ds_data_path = self.ds_path + 'data/'
        os.makedirs(self.ds_data_path, exist_ok=True)
        print(self.ds_data_path)
        self.reader = reader
        self.source = None
        self.filt_cache = {}

    def downsample_ffl(self, ffl_cache: FFLCache):
        segments = [(gs, ge) for (gs, ge) in ffl_cache.segments]
        self.source = ffl_cache.ffl_file

        n_cpu = min(mp.cpu_count() - 1, len(segments))
        mp_pool = mp.Pool(n_cpu)
        with tqdm(total=len(segments)) as progress:
            for i, _ in enumerate(mp_pool.imap_unordered(self.process_segment, segments)):
                progress.update()
        mp_pool.close()
        mp_pool.join()

    def process_segment(self, segment):
        gps_start, gps_stop = segment

        file_name = self.FILE_TEMPLATE.format(f_target=self.f_target,
                                              t_start=int(gps_start),
                                              t_stop=int(gps_stop),
                                              method=self.method)
        file_path = self.ds_data_path + file_name
        with h5py.File(file_path + '.h5', 'w') as h5f:
            for t in np.arange(gps_start, gps_stop, self.FRAME_DURATION):
                self._store_data(h5_file=h5f, t=t, gps_start=gps_start)

    def _store_data(self, h5_file, t, gps_start):
        with FrameFile(self.source).get_frame(t) as ff:
            for adc in ff.iter_adc():
                f_sample = adc.contents.sampleRate
                if f_sample >= 50:
                    channel = str(adc.contents.name)
                    if t == gps_start:
                        ds_data = np.zeros(self.n_target * self.FRAMES_IN_FRAME_FILE)
                        ds_data[0:self.n_target] = self.downsample_adc(adc, f_sample)
                        h5_file.create_dataset(name=channel, data=ds_data)
                    else:
                        i = int((t - gps_start) * self.f_target)
                        j = i + self.n_target
                        h5_file[channel][i:j] = self.downsample_adc(adc, f_sample)

    def downsample_adc(self, adc, f_sample):
        data = FrVect2array(adc.contents.data)
        ds_data = None

        if self.method == 'mean':
            ds_data = self._resample_mean(data)
        elif self.method == 'filt':  # todo: when ds_ratio >= 10-13 do it in steps to prevent numerical error
            ds_data = self._decimate(data, f_sample).astype(np.float64)
        elif self.method == 'filtfilt':
            ds_data = self._decimate(data, f_sample, filtfilt=True).astype(np.float64)
        else:
            LOG.error(f"No implementation found for resampling method '{self.method}'.")

        return ds_data

    def _resample_mean(self, data):
        padding = np.empty(math.ceil(data.size / self.n_target) * self.n_target - data.size)
        padding.fill(np.nan)
        padded_data = np.append(data, padding)
        ds_ratio = len(padded_data) / self.n_target
        return self._n_sample_average(padded_data, ratio=int(ds_ratio))

    @staticmethod
    def _n_sample_average(x: np.array, ratio):
        return np.nanmean(x.reshape(-1, ratio), axis=1)

    def _decimate(self, data, f_sample, filtfilt=False):
        ds_ratio = f_sample / self.f_target

        if math.isclose(ds_ratio, 1):  # f_sample ~= f_target
            return data

        if ds_ratio.is_integer():  # decimate
            if ds_ratio not in self.filt_cache:
                self.filt_cache[ds_ratio] = sig.cheby1(N=self.FILTER_ORDER, rp=0.05, Wn=0.8 / ds_ratio, output='sos')
            if filtfilt:
                return sig.sosfiltfilt(self.filt_cache[ds_ratio], data)[::int(ds_ratio)]
            else:
                return sig.sosfilt(self.filt_cache[ds_ratio], data)[::int(ds_ratio)]
        else:
            return self._resample(data)

    def _resample(self, data):  # Fourier resampling
        return sig.resample(data, self.n_target, window='hamming')
