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

    def __init__(self, source=None):
        self.default_path = get_resource_path(depth=2)
        self.exclude_patterns = None
        self.source = source
        self.frame_file = None

    def set_frame_file(self, ffl_source):
        self.frame_file = ffl_source

    def set_patterns(self, patterns):
        self.exclude_patterns = patterns

    def get_channel_segment(self, channel_name, t_start, t_stop, connection=None) -> ChannelSegment:
        if connection:
            x = TimeSeries.fetch(channel_name, t_start, t_stop, connection=connection)
            channel = Channel(name=channel_name, f_sample=None)
            segment = ChannelSegment(channel=channel, data=x, gps_time=None)
        else:
            if self.frame_file is None:
                self.frame_file = FrameFile(self.source)
            frame = self.frame_file.getChannel(channel_name, t_start, t_stop)
            channel = Channel(name=channel_name, f_sample=frame.fsample, unit=frame.unit)
            segment = ChannelSegment(channel=channel, data=frame.data, gps_time=frame.gps)
        return segment

    def get_available_channels(self, t0) -> [Channel]:
        with FrameFile(self.source).get_frame(t0) as f:
            channels = [Channel(name=str(adc.contents.name),
                                f_sample=adc.contents.sampleRate)
                        for adc in f.iter_adc()]
            if self.exclude_patterns:
                return [c for c in channels if not any(fnmatch(c.name, p) for p in self.exclude_patterns)]
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

        return pd.read_csv(csv_file, usecols=usecols)

