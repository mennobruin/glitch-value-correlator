import numpy as np

from core.config.configuration_manager import ConfigurationManager
from application1.model.channel_segment import ChannelSegment

from virgotools.frame_lib import FrameFile

LOG = ConfigurationManager.get_logger(__name__)


class Decimator:

    def __init__(self, f_target, method='mean'):
        self.f_target = f_target
        self.method = method

    def decimate_gwf(self, gwf_file, segments):

        with FrameFile(gwf_file) as gwf:
            for i, frame in enumerate(gwf):
                print(i, frame)


    def decimate_segment(self, segment: ChannelSegment):
        channel = segment.channel

        ds_ratio = channel.f_sample / self.f_target

        if not ds_ratio.is_integer():
            LOG.warning(f"{channel.name}: sample frequency {channel.f_sample} is not integer divisible by target frequency {self.f_target}.")
        ds_ratio = int(ds_ratio)

        if self.method == 'mean':
            segment.data = self._n_sample_average(segment.data, ds_ratio)
        channel.f_sample = self.f_target
        segment.decimated = True

        return segment

    @staticmethod
    def _n_sample_average(x: np.array, n):
        return x.reshape(-1, n).mean(axis=1)
