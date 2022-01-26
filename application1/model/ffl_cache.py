import numpy as np

from ligo import segments

from application1.handler.data.reader import DataReader


class FFLCache:

    FFL_FORMAT = [('gwf', str, 100), ('gps_start', float), ('duration', float)]
    FFL_COLS = [0, 1, 2]

    def __init__(self, ffl_file, f_target, gps_start, gps_end):
        self.ffl_file = ffl_file
        self.f_target = f_target
        self.gps_start = gps_start
        self.gps_end = gps_end
        self.frames = self._get_frames()
        self.reader = DataReader()

        self.gwf_files = [str(f) for f in self.frames.gwf]
        self.segments = segments.segmentlist(
            segments.segment(gs, ge) for gs, ge in
            zip(self.frames.gps_start, self.frames.gps_start + self.frames.duration)
        )
        self.lookup = dict(zip(self.segments, self.gwf_files))

    def _get_frames(self):
        frames = np.loadtxt(self.ffl_file + '.ffl', dtype=self.FFL_FORMAT, usecols=self.FFL_COLS)
        frames = frames.view(dtype=(np.record, frames.dtype), type=np.recarray)
        end_times = frames.gps_start + frames.duration
        return frames[(end_times > self.gps_start) & (frames.gps_start < self.gps_end)]

    def get_segment(self, request_segment, channel):
        request_segment = segments.segmentlist([request_segment]) & self.segments

        blocks = []
        for seg in request_segment:
            segment = self.segments[self.segments.find(seg)]
            block = self.reader.get(source=self.ffl_file,
                                    channel_name=channel,
                                    t_start=segment[0],
                                    t_stop=segment[1])
            blocks.append(block)
        return blocks