import numpy as np
import os
import re
import sys

from application.config import config_manager

LOG = config_manager.get_logger(__name__)


def iter_segments(subsegs):
    ge_prev = None
    for i, segment in enumerate(subsegs):
        gs, ge = segment
        gap = False
        if ge_prev is not None and ge_prev != gs:  # gap between segments
            LOG.info(f'Gap between segments from {ge_prev} to {gs}')
            gap = True
        yield i, segment, gap
        ge_prev = ge


def slice_triggers_in_segment(triggers, gps_start, gps_end, pipeline):
    if pipeline.NAME == 'local':
        return slice(*np.searchsorted(triggers['GPStime'], (gps_start, gps_end)))
    else:
        return slice(*np.searchsorted(triggers, (gps_start, gps_end)))


def count_triggers_in_segment(triggers, label, gps_start, gps_end, pipeline):
    if pipeline.NAME == 'local':
        i_start, i_end = np.searchsorted(triggers[triggers.label == label]['GPStime'], (gps_start, gps_end))
    else:
        i_start, i_end = np.searchsorted(triggers, (gps_start, gps_end))
    return i_end - i_start


def check_extension(file_name, extension):
    root, ext = os.path.splitext(file_name)
    if not ext:
        return file_name + extension
    if ext != extension:
        LOG.warning(f'Unexpected extension {ext} in {file_name}. Expected {extension}.')
    return file_name


def split_file_name(file_name):
    f_sample, gps_start, gps_end, _ = tuple(int(s) for s in re.split('(\d+)', file_name) if s.isnumeric())
    return f_sample, gps_start, gps_end


def exit_on_error():
    sys.exit(1)


def almost_int(float_val):
    return abs(float_val - round(float_val)) % 1 < 0.0001


def create_dir_if_not_exists(path_to_dir):
    if not os.path.exists(path_to_dir):
        os.mkdir(path_to_dir)
        LOG.info(f'Created new directory {path_to_dir}')
