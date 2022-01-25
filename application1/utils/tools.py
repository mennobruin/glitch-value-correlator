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
