import time
import numpy as np

from core.config.configuration_manager import ConfigurationManager
from application1.model.channel_segment import ChannelSegment

LOG = ConfigurationManager.get_logger(__name__)


class Decimator:

    def __init__(self, f_target=50, method='mean', verbose=False):
        self.f_target = f_target
        self.method = method
        self.verbose = verbose

    def decimate(self, segment: ChannelSegment):
        if self.verbose:
            LOG.info(f"Decimating {segment.data.size} data points with target frequency {self.f_target}Hz...")
            t0 = time.time()
        if self.f_target > segment.f_sample:
            return segment

        ds_ratio = segment.f_sample / self.f_target

        if not ds_ratio.is_integer():
            LOG.warning(f"Size of input data {segment.data.size} is not integer divisible by target frequency {self.f_target}.")
        ds_ratio = int(ds_ratio)

        if self.method == 'mean':
            segment.data = self._n_sample_average(segment.data, ds_ratio)
        segment.f_sample = self.f_target
        segment.decimated = True

        if self.verbose:
            LOG.info(f"Decimating complete. Time elapsed: {time.time() - t0:.1f}s")

        return segment

    @staticmethod
    def _n_sample_average(x: np.array, n):
        return x.reshape(-1, n).mean(axis=1)
