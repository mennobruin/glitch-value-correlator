import numpy as np

from core.config.configuration_manager import ConfigurationManager

LOG = ConfigurationManager.get_logger(__name__)


class Decimator:

    def __init__(self):
        pass

    def decimate(self, input_data: np.array, target_frequency=50, method='mean'):

        input_size = len(input_data)
        ds_ratio = input_size / target_frequency

        if not ds_ratio.is_integer():
            LOG.warning(f"Size of input data {input_size} is not integer divisible by target frequency {target_frequency}.")
        ds_ratio = int(ds_ratio)

        if method == 'mean':
            return self._n_sample_average(input_data, ds_ratio)

    @staticmethod
    def _n_sample_average(x: np.array, n):
        return x.reshape(-1, n).mean(axis=1)
