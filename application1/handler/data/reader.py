import os

from fnmatch import fnmatch

import pandas as pd
from gwpy.timeseries import TimeSeries
from virgotools.frame_lib import FrameFile

from application1.model.channel_segment import ChannelSegment
from application1.model.channel import Channel
from application1.utils import get_resource_path, check_extension
from core.config.configuration_manager import ConfigurationManager

LOG = ConfigurationManager.get_logger(__name__)


class DataReader:

    def __init__(self):
        self.default_path = get_resource_path(depth=2)
        self.frame_file = None

    def get_channel_segment(self, channel_name, t_start, t_stop, source='raw', connection=None) -> ChannelSegment:
        if connection:
            x = TimeSeries.fetch(channel_name, t_start, t_stop, connection=connection)
            channel = Channel(name=channel_name, f_sample=None)
            segment = ChannelSegment(channel=channel, data=x, gps_time=None)
        else:
            if not self.frame_file:
                self.frame_file = FrameFile(source)
            frame = self.frame_file.getChannel(channel_name, t_start, t_stop)
            channel = Channel(name=channel_name, f_sample=frame.fsample, unit=frame.unit)
            segment = ChannelSegment(channel=channel, data=frame.data, gps_time=frame.gps)
        return segment

    @staticmethod
    def get_available_channels(source, t0, exclude_patterns: list = None) -> [Channel]:
        LOG.info(f"Fetching available channels from {source}")
        with FrameFile(source) as ffl:
            with ffl.get_frame(t0) as f:
                channels = [Channel(name=str(adc.contents.name),
                                    f_sample=adc.contents.sampleRate)
                            for adc in f.iter_adc()]
                if exclude_patterns:
                    return [c for c in channels if not any(fnmatch(c.name, p) for p in exclude_patterns)]
                else:
                    return channels

    def load_csv(self, csv_file, usecols=None) -> pd.DataFrame:
        csv_file = check_extension(csv_file, extension='.csv')

        LOG.info(f"Loading {csv_file}")
        if not os.path.isfile(csv_file):
            csv_file = self.default_path + 'csv/' + csv_file
            if not os.path.isfile(csv_file):
                LOG.error(f"Unable to load csv_file: {csv_file}, check if the file exists.")
                raise FileNotFoundError

        print(type(csv_file), csv_file)
        print(type(usecols), usecols)
        return pd.read_csv(csv_file, usecols=usecols)

