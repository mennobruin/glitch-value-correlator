import numpy as np

from application1.handler.data.reader.csv import CSVReader
from core.config import ConfigurationManager

LOG = ConfigurationManager.get_logger(__name__)


class DefaultPipeline:

    GPS_TIME = 'GPStime'
    LABEL = 'label'

    def __init__(self, trigger_file, trigger_type=None):
        self.reader = CSVReader()
        self.triggers = self.load_triggers(trigger_file, trigger_type)
        LOG.info(f'Found {self.triggers.shape[0]} triggers of type {trigger_type if trigger_type else "[all]"}.')

    def load_triggers(self, path_to_csv, trigger_type):
        triggers = self.reader.load_csv(path_to_csv, usecols=[self.GPS_TIME, self.LABEL])
        if trigger_type:
            triggers = triggers.loc[triggers[self.LABEL] == trigger_type]
        sorted_triggers = triggers.sort_values(self.GPS_TIME)
        return sorted_triggers.values.flatten()

    def get_segment(self, gps_start, gps_end) -> np.ndarray:
        i_start, i_end = np.searchsorted(self.triggers, (gps_start, gps_end))
        return self.triggers[i_start:i_end]
