import os
import numpy as np

from ligo import segments

from application1.utils import split_file_name
from resources.constants import RESOURCE_DIR

from application1.config import config_manager

LOG = config_manager.get_logger(__name__)


class BaseReader

    RECORD_STRUCTURE = [('file', str, 100), ('gps_start', float), ('gps_end', float)]

    def __init__(self, gps_start, gps_end, exclude_patterns):
        self.default_path = RESOURCE_DIR
        self.gps_start = gps_start
        self.gps_end = gps_end
        self.exclude_patterns = exclude_patterns
        self.cache = None
        self.records = None
        self.files = None
        self.segments = None

    def _reset_cache(self):
        self.cache.close()
        self.cache = None

    def _check_path_exists(self, file_loc, file):
        if not os.path.isfile(file):
            file = self.default_path + file_loc + file
            if not os.path.isfile(file):
                LOG.error(f"Unable to load file: {file}, check if the file exists.")
                raise FileNotFoundError
        return file

    @staticmethod
    def _get_segments(records):
        return segments.segmentlist(
            segments.segment(gs, ge) for gs, ge in
            zip(records.gps_start, records.gps_end)
        )
