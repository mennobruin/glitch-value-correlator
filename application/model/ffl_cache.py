"""
    Data handling for FFL files. Uses the FFL reader.
"""

import numpy as np
from framel import frgetvect1d
from ligo import segments

from application.config import config_manager
from application.handler.data.reader.ffl import FrameFileReader
from application.utils import check_extension, exit_on_error

LOG = config_manager.get_logger(__name__)


class FFLCache:

    FFL_FORMAT = [('gwf', str, 100), ('gps_start', float), ('duration', float)]
    FFL_COLS = [0, 1, 2]

    def __init__(self, ffl_file, gps_start, gps_end, bl_patterns=None):
        self.ffl_file = check_extension(ffl_file, extension='.ffl')
        self.gps_start = gps_start
        self.gps_end = gps_end
        self.frames = self._get_frames()
        if self.frames.size == 0:
            LOG.error(f'No data found from {gps_start} to {gps_end} in {ffl_file}.')
            exit_on_error()
        self.reader = FrameFileReader(source=self.ffl_file,
                                      gps_start=gps_start,
                                      gps_end=gps_end,
                                      exclude_patterns=bl_patterns)

        self.gwf_files = [str(f) for f in self.frames.gwf]
        self.segments = segments.segmentlist(
            segments.segment(gs, ge) for gs, ge in
            zip(self.frames.gps_start, self.frames.gps_start + self.frames.duration)
        )
        self.lookup = dict(zip(self.segments, self.gwf_files))

    def _get_frames(self):
        frames = np.loadtxt(self.ffl_file, dtype=self.FFL_FORMAT, usecols=self.FFL_COLS)
        frames = frames.view(dtype=(np.record, frames.dtype), type=np.recarray)
        end_times = frames.gps_start + frames.duration
        return frames[(end_times > self.gps_start) & (frames.gps_start < self.gps_end)]

    def get_data_from_segment(self, request_segment, channel):
        request_segment = segments.segmentlist([request_segment]) & self.segments

        blocks = []
        for seg in request_segment:
            i_segment = self.segments.find(seg)
            segment = self.segments[i_segment]
            gwf_file = self.gwf_files[i_segment]
            block = frgetvect1d(gwf_file, channel, segment[0], abs(segment))[0].astype(float)
            blocks.append(block)
        return np.concatenate(blocks)
