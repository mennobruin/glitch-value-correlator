import pandas as pd
import pathlib
import os
import time

from gwpy.timeseries import TimeSeries
from virgotools.frame_lib import getChannel, FrameFile

from core.config.configuration_manager import ConfigurationManager
from model.channel import Channel

LOG = ConfigurationManager.get_logger(__name__)


class DataReader:
    def __init__(self):
        self.default_path = str(pathlib.Path(__file__).parents[2].resolve()) + "\\resources\\"

    @staticmethod
    def get(channel, t_start, t_stop, source='raw', connection=None, verbose=False) -> Channel:
        LOG.info(f"Fetching data from {channel}...")
        t0 = time.time()
        if connection:
            x = TimeSeries.fetch(channel, t_start, t_stop, connection=connection, verbose=verbose)
            c = Channel(x=x, dx=None, gps_time=None, unit=None)
        else:
            with FrameFile(source) as ffl:
                frame = ffl.getChannel(channel, t_start, t_stop)
            c = Channel(x=frame.data, dx=frame.fsample, gps_time=frame.gps, unit=frame.unit)
        LOG.info(f"Fetched data from {channel}, time elapsed: {time.time() - t0:.1f}s")
        return c

    def load_csv(self, csv_file) -> pd.DataFrame:
        LOG.info(f"Loading {csv_file}")
        if not os.path.isfile(csv_file):
            csv_file = self.default_path + 'csv\\' + csv_file
            if not os.path.isfile(csv_file):
                LOG.error(f"Unable to load csv_file: {csv_file}. Check if the file exists.")
                raise FileNotFoundError

        with open(csv_file, 'r') as f:
            return pd.read_csv(f)
