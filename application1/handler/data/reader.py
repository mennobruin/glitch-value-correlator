import pandas as pd
import os
import time

from fnmatch import fnmatch
from gwpy.timeseries import TimeSeries
from virgotools.frame_lib import getChannel, FrameFile

from core.config.configuration_manager import ConfigurationManager
from application1.model.segment import Segment
from application1.utils import get_resource_path

LOG = ConfigurationManager.get_logger(__name__)


class DataReader:

    def __init__(self):
        self.default_path = get_resource_path(depth=2)

    @staticmethod
    def get_channel(channel_name, t_start, t_stop, source='raw', connection=None, verbose=False) -> Segment:
        if verbose:
            LOG.info(f"Fetching data from {channel_name}...")
            t0 = time.time()
        if connection:
            x = TimeSeries.fetch(channel_name, t_start, t_stop, connection=connection, verbose=verbose)
        else:
            with FrameFile(source) as ffl:
                s = Segment(channel=channel_name,
                            x=x,
                            f_sample=None,
                            gps_time=None,
                            duration=None,
                            unit=None)
                frame = ffl.getChannel(channel_name, t_start, t_stop)
            s = Segment(channel=channel_name,
                        x=frame.data,
                        f_sample=frame.fsample,
                        gps_time=frame.gps,
                        duration=frame.dt,
                        unit=frame.unit)
        if verbose:
            LOG.info(f"Fetched data from {source}, time elapsed: {time.time() - t0:.1f}s")
        return s

    @staticmethod
    def get_available_channels(source, t0, exclude_patterns: list = None):
        LOG.info(f"Fetching available channels from {source}")
        with FrameFile(source) as ffl:
            with ffl.get_frame(t0) as f:
                channels = [str(adc.contents.name) for adc in f.iter_adc()]
                if exclude_patterns:
                    return [c for c in channels if not any(fnmatch(c, p) for p in exclude_patterns)]
                else:
                    return channels

    def load_csv(self, csv_file, usecols=None) -> pd.DataFrame:
        root, ext = os.path.splitext(csv_file)
        if not ext:
            ext = '.csv'
        csv_file = root + ext

        LOG.info(f"Loading {csv_file}")
        if not os.path.isfile(csv_file):
            csv_file = self.default_path + 'csv/' + csv_file
            if not os.path.isfile(csv_file):
                LOG.error(f"Unable to load csv_file: {csv_file}, check if the file exists.")
                raise FileNotFoundError

        print(type(csv_file), csv_file)
        print(type(usecols), usecols)
        return pd.read_csv(csv_file, usecols=usecols)

