import time
import numpy as np

from core.config.configuration_manager import ConfigurationManager

LOG = ConfigurationManager.get_logger(__name__)


class Decimator:

    def __init__(self):
        pass

    def decimate(self, input_data: np.array, input_frequency, target_frequency=50, method='mean'):
        LOG.info(f"Decimating {len(input_data)} data points with target frequency {target_frequency}Hz...")
        t0 = time.time()

        ds_ratio = input_frequency / target_frequency

        if not ds_ratio.is_integer():
            LOG.warning(f"Size of input data {len(input_data)} is not integer divisible by target frequency {target_frequency}.")
        ds_ratio = int(ds_ratio)

        output_data = None
        if method == 'mean':
            output_data = self._n_sample_average(input_data, ds_ratio)

        LOG.info(f"Decimating complete. Time elapsed: {time.time() - t0:.1f}s")
        return output_data

    @staticmethod
    def _n_sample_average(x: np.array, n):
        return x.reshape(-1, n).mean(axis=1)
