import numpy as np
import os
import h5py
import math
import multiprocessing as mp

from tqdm import tqdm
from scipy.signal import sosfiltfilt, sosfilt, resample, cheby1

from core.config.configuration_manager import ConfigurationManager
from application1.utils import get_resource_path
from application1.model.channel_segment import ChannelSegment
from application1.model.ffl_cache import FFLCache
from application1.handler.data.reader import DataReader

from virgotools.frame_lib import FrameFile, FrVect2array

LOG = ConfigurationManager.get_logger(__name__)


class Resampler:

    FILE_TEMPLATE = 'excavator_f{f_target}_gs{t_start}_ge{t_stop}_{method}'
    FILTER_ORDER = 4
    FRAME_DURATION = 10

    def __init__(self, f_target, reader: DataReader, method='mean'):
        self.f_target = f_target
        self.method = method
        self.resource_path = get_resource_path(depth=1)
        self.ds_path = self.resource_path + 'ds_data/'
        self.ds_data_path = self.ds_path + 'data/'
        os.makedirs(self.ds_data_path, exist_ok=True)
        print(self.ds_data_path)
        self.reader = reader
        self.channels = None
        self.source = None

    def downsample_ffl(self, ffl_cache: FFLCache):
        segments = [(gs, ge) for (gs, ge) in ffl_cache.segments]
        channels = self.reader.get_available_channels(t0=ffl_cache.gps_start)
        self.channels = [c for c in channels if c.f_sample > self.f_target]
        self.source = ffl_cache.ffl_file

        for segment in tqdm(segments):
            self.process_segment(segment)

        # n_cpu = min(mp.cpu_count() - 1, len(segments))
        # with mp.Pool(n_cpu) as mp_pool:
        #     with tqdm(len(segments)) as progress:
        #         for i, _ in mp_pool.imap_unordered(self.process_segment, segments):
        #             progress.update()

    def process_segment(self, segment):
        gps_start, gps_stop = segment
        ds_data = np.array([])

        for t in np.arange(gps_start, gps_stop, self.FRAME_DURATION):
            frame_data = []
            with FrameFile(self.source).get_frame(t) as f:
                for adc in f.iter_adc():
                    f_sample = adc.contents.sampleRate
                    if f_sample >= 50:
                        frame_data.append(self.downsample_adc(adc, f_sample))
            ds_data = np.hstack((ds_data, frame_data))

        file_name = self.FILE_TEMPLATE.format(f_target=self.f_target,
                                              t_start=int(gps_start),
                                              t_stop=int(gps_stop),
                                              method=self.method)
        file_path = self.ds_data_path + file_name
        with h5py.File(file_path + '.h5', 'w') as f:
            f.create_dataset(name='data', data=ds_data)
            f.create_dataset(name='channels', data=np.array([c.name for c in self.channels], dtype='S'))

    def downsample_adc(self, adc, f_sample):
        data = FrVect2array(adc.contents.data)
        ds_data = None

        if self.method == 'mean':
            padding = np.empty(math.ceil(data.size / self.f_target) * self.f_target - data.size)
            padding.fill(np.nan)
            padded_data = np.append(data, padding)
            ds_ratio = len(padded_data) / (self.FRAME_DURATION * self.f_target)
            ds_data = self._n_sample_average(padded_data, ratio=int(ds_ratio))
        elif self.method == 'decimate':
            ds_data = self._decimate(data, f_sample)
        else:
            LOG.error(f"No implementation found for resampling method '{self.method}'.")

        return ds_data

    @staticmethod
    def _n_sample_average(x: np.array, ratio):
        return np.nanmean(x.reshape(-1, ratio), axis=1)

    def _decimate(self, data, f_sample):
        ds_ratio = f_sample / self.f_target

        if math.isclose(ds_ratio, 1):  # f_sample ~= f_target
            return data

        if ds_ratio.is_integer():  # decimate
            filt = cheby1(N=self.FILTER_ORDER, rp=0.05, Wn=0.8 / ds_ratio, output='sos')
            return sosfiltfilt(filt, data)[::int(ds_ratio)]
        else:  # Fourier resampling
            return resample(data, len(data), window='hamming')
