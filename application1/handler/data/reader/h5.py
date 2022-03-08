import numpy as np
import h5py
import os
from ligo import segments

from .base import BaseReader

from application1.utils import check_extension, split_file_name, RESOURCE_PATH


class H5Reader(BaseReader):

    RECORD_STRUCTURE = np.dtype([('h5_file', str), ('gps_start', int), ('gps_end', int)])
    H5_DIR = RESOURCE_PATH + 'ds_data/data/'
    H5 = '.h5'

    def __init__(self, gps_start, gps_end):
        super(H5Reader, self).__init__()
        self.h5_file = None
        self.gps_start = gps_start
        self.gps_end = gps_end
        self.h5_files = self._get_files()
        self.segments = segments.segmentlist(
            segments.segment(gs, ge) for gs, ge in
            zip(self.h5_files.gps_start, self.h5_files.gps_end)
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.h5_file.close()

    def _get_files(self):
        h5_files = [f for f in os.listdir(self.H5_DIR) if f.endswith(self.H5)]
        records = []
        for file in h5_files:
            _, gps_start, gps_end = split_file_name(file)
            records.append((file, gps_start, gps_end))
        records = np.array(records, dtype=self.RECORD_STRUCTURE)
        records = records.view(dtype=(np.record, records.dtype), type=np.recarray)
        return records

    def load_h5(self, h5_file):
        h5_file = check_extension(h5_file, extension=self.H5)

        if self.h5_file is None or os.path.dirname(self.h5_file.filename) is not h5_file:
            h5_file = self._check_path_exists(file_loc=self.H5_DIR, file=h5_file)
            self.h5_file = h5py.File(h5_file, 'r')

    def get_channel(self, channel_name):
        return self.h5_file[channel_name]

    def get_data_from_segments(self, request_segments):
        request_segments = segments.segmentlist([request_segments]) & self.segments

        for seg in request_segments:
            i_segment = self.segments.find(seg)
            segment = self.segments[i_segment]
            h5_file = self.h5_files[i_segment]
            # print(segment)
            # print(h5_file)
