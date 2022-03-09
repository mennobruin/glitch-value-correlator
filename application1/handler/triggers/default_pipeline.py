import numpy as np

from application1.handler.data.reader.csv import CSVReader
from core.config import ConfigurationManager

LOG = ConfigurationManager.get_logger(__name__)


class DefaultPipeline:

    GPS_TIME = 'GPStime'

    def __init__(self, trigger_file):
        self.reader = CSVReader()
        self.triggers = self.load_triggers(trigger_file)
        LOG.info(f'Found {self.triggers.shape[0]} triggers.')

    def load_triggers(self, path_to_csv):
        sorted_triggers = self.reader.load_csv(path_to_csv, usecols=[self.GPS_TIME]).sort_values(self.GPS_TIME)
        return sorted_triggers.values.flatten()

    def get_segment(self, gps_start, gps_end) -> np.ndarray:
        i_start, i_end = np.searchsorted(self.triggers, (gps_start, gps_end))
        return self.triggers[i_start:i_end]
