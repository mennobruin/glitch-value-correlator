from fnmatch import fnmatch

from gwpy.timeseries import TimeSeries
from virgotools.frame_lib import FrameFile

from .base import BaseReader
from application1.model.channel_segment import ChannelSegment
from application1.model.channel import Channel


class FrameFileReader(BaseReader):

    def __init__(self, source=None):
        super(FrameFileReader, self).__init__()
        self.exclude_patterns = None
        self.source = source

    def set_patterns(self, patterns):
        self.exclude_patterns = patterns

    def get_channel_segment(self, channel_name, t_start, t_stop, connection=None) -> ChannelSegment:
        if connection:
            x = TimeSeries.fetch(channel_name, t_start, t_stop, connection=connection)
            channel = Channel(name=channel_name, f_sample=None)
            segment = ChannelSegment(channel=channel, data=x, gps_time=None)
        else:
            with FrameFile(self.source) as ff:
                frame = ff.getChannel(channel_name, t_start, t_stop)
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
