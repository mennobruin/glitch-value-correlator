import pandas as pd
import pathlib
import os
import time

from fnmatch import fnmatch
from gwpy.timeseries import TimeSeries
from virgotools.frame_lib import getChannel, FrameFile

from core.config.configuration_manager import ConfigurationManager
from application1.model.segment import Segment

LOG = ConfigurationManager.get_logger(__name__)


class DataReader:
    def __init__(self):
        self.default_path = str(pathlib.Path(__file__).parents[2].resolve()) + "\\resources\\"

    @staticmethod
    def get(channel_name, t_start, t_stop, source='raw', connection=None, verbose=False) -> Segment:
        if verbose:
            LOG.info(f"Fetching data from {channel_name}...")
            t0 = time.time()
        if connection:
            x = TimeSeries.fetch(channel_name, t_start, t_stop, connection=connection, verbose=verbose)
            s = Segment(channel=channel_name,
                        x=x,
                        dt=None,
                        f_sample=None,
                        gps_time=None,
                        unit=None)
        else:
            with FrameFile(source) as ffl:
                frame = ffl.getChannel(channel_name, t_start, t_stop)
            s = Segment(channel=channel_name,
                        x=frame.data,
                        dt=frame.dt,
                        f_sample=frame.fsample,
                        gps_time=frame.gps,
                        unit=frame.unit)
        if verbose:
            LOG.info(f"Fetched data from {source}, time elapsed: {time.time() - t0:.1f}s")
        return s

    @staticmethod
    def get_available_channels(source, t0, patterns: list = None):
        LOG.info(f"Fetching available channels from {source}")
        with FrameFile(source) as ffl:
            with ffl.get_frame(t0) as f:
                channels = [str(adc.contents.name) for adc in f.iter_adc()]
                if patterns:
                    return [c for c in channels if not any(fnmatch(c, p) for p in patterns)]
                else:
                    return channels

    def load_csv(self, csv_file) -> pd.DataFrame:
        LOG.info(f"Loading {csv_file}")
        if not os.path.isfile(csv_file):
            csv_file = self.default_path + 'csv\\' + csv_file
            if not os.path.isfile(csv_file):
                LOG.error(f"Unable to load csv_file: {csv_file}. Check if the file exists.")
                raise FileNotFoundError

        with open(csv_file, 'r') as f:
            return pd.read_csv(f)
