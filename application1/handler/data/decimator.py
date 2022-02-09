import time
import numpy as np

from core.config.configuration_manager import ConfigurationManager
from application1.model.segment import Segment
from application1.utils import get_resource_path

LOG = ConfigurationManager.get_logger(__name__)


class Decimator:

    def __init__(self, f_target=50, method='mean', verbose=False):
        self.f_target = f_target
        self.method = method
        self.verbose = verbose
        self.default_path = get_resource_path(depth=2)

    def decimate(self, segment: Segment):
        if self.verbose:
            LOG.info(f"Decimating {segment.x.size} data points with target frequency {self.f_target}Hz...")
        t0 = time.time()

        ds_ratio = segment.f_sample / self.f_target

        if not ds_ratio.is_integer():
            LOG.warning(f"Size of input data {segment.x.size} is not integer divisible by target frequency {self.f_target}.")
        ds_ratio = int(ds_ratio)

        if self.method == 'mean':
            segment.x = self._n_sample_average(segment.x, ds_ratio)
        segment.f_sample = self.f_target
        segment.decimated = True

        if self.verbose:
            LOG.info(f"Decimating complete. Time elapsed: {time.time() - t0:.1f}s")
        return segment

    @staticmethod
    def _n_sample_average(x: np.array, n):
        return x.reshape(-1, n).mean(axis=1)
