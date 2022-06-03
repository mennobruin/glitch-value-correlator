import os
from fnmatch import fnmatch
from sys import exit

import numpy as np
from ligo import segments
from virgotools.frame_lib import FrameFile, FrVect2array
from virgotools import getChannel
from framel import frgetvect1d

from application1.config import config_manager
from application1.model.channel import Channel, ChannelSegment
from .base import BaseReader

LOG = config_manager.get_logger(__name__)


class FrameFileReader(BaseReader):

    FFL_DIR = '/virgoData/ffl/'
    FFL = '.ffl'

    def __init__(self, source, gps_start, gps_end, exclude_patterns=None):
        super(FrameFileReader, self).__init__(gps_start, gps_end, exclude_patterns)
        self.source = source
        self.records = self._get_records(self.source)
        self.files = [str(f) for f in self.records.file]
        self.segments = self._get_segments()

    def _get_records(self, file):
        records = np.loadtxt(file, dtype=self.RECORD_STRUCTURE)
        records = records.view(dtype=(np.record, records.dtype), type=np.recarray)
        records.gps_end = records.gps_start + records.gps_end
        return records[(records.gps_end > self.gps_start) & (records.gps_start < self.gps_end)]

    def _get_segments(self):
        return segments.segmentlist(
            segments.segment(gs, ge) for gs, ge in
            zip(self.records.gps_start, self.records.gps_end)
        )

    @staticmethod
    def get_channel_segment(file, channel_name, t_start, t_stop) -> ChannelSegment:
        with FrameFile(file) as ff:
            frame = ff.getChannel(channel_name, t_start, t_stop)
        channel = Channel(name=channel_name, f_sample=frame.fsample, unit=frame.unit)
        segment = ChannelSegment(channel=channel, data=frame.data, gps_time=frame.gps)
        return segment

    @staticmethod
    def get_channel_data(gwf_file, segment, channel):
        with FrameFile(gwf_file) as ff:
            frame = ff.getChannel(channel.name, *segment)
        np.set_printoptions(threshold=np.inf)
        print(frgetvect1d(gwf_file, channel, segment[0], abs(segment))[0].astype(float))
        exit(0)
        return frame.data

    def get_available_channels(self, t0=None, f_target=None) -> [Channel]:
        t0 = t0 if t0 else self.gps_start
        with FrameFile(self.source).get_frame(t0) as f:
            channels = [Channel(name=str(adc.contents.name),
                                f_sample=adc.contents.sampleRate)
                        for adc in f.iter_adc()]
            if f_target:
                channels = [c for c in channels if c.f_sample == f_target]
            if self.exclude_patterns:
                channels = [c for c in channels if not any(fnmatch(c.name, p) for p in self.exclude_patterns)]
            return channels

    def get_data_from_segments(self, request_segment, channel_name):
        request_segments = segments.segmentlist([request_segment]) & self.segments

        all_data = []
        for seg in request_segments:
            i_segment = self.segments.find(seg)
            file = self.files[i_segment]
            channel_data = self.get_channel_data(gwf_file=file, segment=seg, channel=channel_name)
            all_data.append(channel_data)

        return np.concatenate(all_data)
