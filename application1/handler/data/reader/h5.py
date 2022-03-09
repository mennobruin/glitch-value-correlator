import numpy as np
import h5py
import os
from ligo import segments

from .base import BaseReader

from application1.utils import check_extension, split_file_name, RESOURCE_PATH
from core.config import ConfigurationManager

LOG = ConfigurationManager.get_logger(__name__)


class H5Reader(BaseReader):

    RECORD_STRUCTURE = [('file', str, 100), ('gps_start', int), ('gps_stop', int)]
    H5_DIR = 'ds_data/data/'
    H5 = '.h5'

    def __init__(self, gps_start, gps_end):
        super(H5Reader, self).__init__()
        self.h5_cache = None
        self.gps_start = gps_start
        self.gps_end = gps_end
        self.h5_records = self._get_records()
        self.h5_files = self.h5_records.file
        self.segments = segments.segmentlist(
            segments.segment(gs, ge) for gs, ge in
            zip(self.h5_records.gps_start, self.h5_records.gps_end)
        )

    def _get_records(self):
        h5_files = [f for f in os.listdir(RESOURCE_PATH + self.H5_DIR) if f.endswith(self.H5)]
        records = []
        for file in h5_files:
            _, gps_start, gps_end = split_file_name(file)
            records.append((file, gps_start, gps_end))
        records = np.array(records, dtype=self.RECORD_STRUCTURE)
        records = records.view(dtype=(np.record, records.dtype), type=np.recarray)
        return records[(records.gps_stop > self.gps_start) & (records.gps_start < self.gps_end)]

    def reset_cache(self):
        self.h5_cache.close()
        self.h5_cache = None

    def load_h5(self, h5_file):
        if self.h5_cache is None:
            h5_file = check_extension(h5_file, extension=self.H5)
            LOG.info(f'loading {h5_file}')
            h5_file = self._check_path_exists(file_loc=self.H5_DIR, file=h5_file)
            self.h5_cache = h5py.File(h5_file, 'r')

    def get_channel_from_file(self, file, channel_name):
        self.load_h5(file)
        return self.h5_cache[channel_name]

    def get_available_channels(self, file=None):
        file = file if file is not None else self.h5_files[0]
        self.load_h5(file)
        return list(self.h5_cache.keys())

    def get_data_from_segments(self, request_segment, channel_name):
        request_segments = segments.segmentlist([request_segment]) & self.segments
        print(request_segment)
        print(request_segments)

        all_data = []
        for seg in request_segments:
            i_segment = self.segments.find(seg)
            h5_file = self.h5_files[i_segment]
            channel_data = self.get_channel_from_file(h5_file, channel_name)
            all_data.append(channel_data)

        return np.concatenate(all_data)


