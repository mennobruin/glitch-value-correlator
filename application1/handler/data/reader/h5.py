import os
from fnmatch import fnmatch

import h5py
import numpy as np
from ligo import segments

from application1.config import config_manager
from application1.utils import check_extension, exit_on_error, split_file_name
from resources.constants import RESOURCE_DIR
from .base import BaseReader

LOG = config_manager.get_logger(__name__)


class H5Reader(BaseReader):

    H5_DIR = 'ds_data/data/'
    H5 = '.h5'

    def __init__(self, gps_start, gps_end, exclude_patterns=None):
        super(H5Reader, self).__init__(gps_start, gps_end, exclude_patterns)
        self.records = self._get_records(loc=self.default_path + self.H5_DIR, ext=self.H5)
        self.files = [str(f) for f in self.records.file]
        self.segments = self._get_segments()

    def _get_records(self, loc, ext):
        files = sorted([f for f in os.listdir(loc) if f.endswith(ext)])
        records = []
        for file in files:
            _, gps_start, gps_end = split_file_name(file)
            records.append((file, gps_start, gps_end))
        records = np.array(records, dtype=self.RECORD_STRUCTURE)
        records = records.view(dtype=(np.record, records.dtype), type=np.recarray)
        return records[(records.gps_end > self.gps_start) & (records.gps_start < self.gps_end)]

    def _get_segments(self):
        return segments.segmentlist(
            segments.segment(gs, ge) for gs, ge in
            zip(self.records.gps_start, self.records.gps_end)
        )

    def load(self, file, channel=None):
        if self.records.size == 0:
            LOG.error(f'No data found from {self.gps_start} to {self.gps_end} in {RESOURCE_DIR + self.H5_DIR}')
            exit_on_error()
        if not self.cache:
            file = check_extension(file, extension=self.H5)
            file = self._check_path_exists(file_loc=self.H5_DIR, file=file)
            try:
                self.cache = h5py.File(file, 'r')
            except OSError as e:
                LOG.error(f'Exception caught while trying to load {file}: {e}')
                LOG.info(f'The HDF5 file {file} might have corrupted, try resampling the data.')
                exit_on_error()
        elif channel not in self.cache:
            self._reset_cache()
            self.load(file, channel)

    def get_channel_from_file(self, file, channel_name):
        self.load(file, channel_name)
        return self.cache[channel_name]

    def get_available_channels(self, file=None):
        file = file if file is not None else self.files[0]
        self.load(file)

        if self.exclude_patterns:
            return [c for c in self.cache.keys() if not any(fnmatch(c, p) for p in self.exclude_patterns)]
        else:
            return list(self.cache.keys())

    def get_data_from_segments(self, request_segment, channel_name):
        request_segments = segments.segmentlist([request_segment]) & self.segments

        all_data = []
        for seg in request_segments:
            i_segment = self.segments.find(seg)
            h5_file = self.files[i_segment]
            try:
                channel_data = self.get_channel_from_file(h5_file, channel_name)
            except KeyError:
                return None
            all_data.append(channel_data)

        return np.concatenate(all_data)
