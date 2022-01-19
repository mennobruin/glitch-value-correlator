import time
import numpy as np

from core.config.configuration_manager import ConfigurationManager
from application1.model.segment import Segment

LOG = ConfigurationManager.get_logger(__name__)


class Decimator:

    def __init__(self):
        pass

    def decimate(self, segment: Segment, target_frequency=50, method='mean'):
        LOG.info(f"Decimating {segment.x.size} data points with target frequency {target_frequency}Hz...")
        t0 = time.time()

        ds_ratio = segment.f_sample / target_frequency

        if not ds_ratio.is_integer():
            LOG.warning(f"Size of input data {segment.x.size} is not integer divisible by target frequency {target_frequency}.")
        ds_ratio = int(ds_ratio)

        if method == 'mean':
            segment.x = self._n_sample_average(segment.x, ds_ratio)
        segment.f_sample = target_frequency
        segment.decimated = True

        LOG.info(f"Decimating complete. Time elapsed: {time.time() - t0:.1f}s")
        return segment

    @staticmethod
    def _n_sample_average(x: np.array, n):
        return x.reshape(-1, n).mean(axis=1)
