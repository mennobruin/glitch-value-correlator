import numpy as np

from core.config import ConfigurationManager

LOG = ConfigurationManager.get_logger(__name__)


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


def slice_triggers_in_segment(triggers, gps_start, gps_end):
    return slice(*np.searchsorted(triggers, (gps_start, gps_end)))


def count_triggers_in_segment(triggers, gps_start, gps_end):
    i_start, i_end = np.searchsorted(triggers, (gps_start, gps_end))
    return i_end - i_start
