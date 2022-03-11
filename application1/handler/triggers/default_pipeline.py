import numpy as np

from application1.handler.data.reader.csv import CSVReader
from application1.config import config_manager

LOG = config_manager.get_logger(__name__)


class DefaultPipeline:

    GPS_TIME = 'GPStime'
    LABEL = 'label'

    def __init__(self, trigger_file, trigger_type):
        self.reader = CSVReader()
        self.trigger_type = trigger_type
        self.triggers = self.load_triggers(trigger_file)

    def load_triggers(self, path_to_csv):
        triggers = self.reader.load_csv(path_to_csv, usecols=[self.GPS_TIME, self.LABEL])
        if self.trigger_type:
            triggers = triggers.loc[triggers[self.LABEL] == self.trigger_type]
        sorted_triggers = triggers.sort_values(self.GPS_TIME)
        return sorted_triggers[self.GPS_TIME].values.flatten()

    def get_segment(self, gps_start, gps_end) -> np.ndarray:
        i_start, i_end = np.searchsorted(self.triggers, (gps_start, gps_end))
        LOG.info(f'Found {self.triggers.shape[0]} triggers of type {self.trigger_type if self.trigger_type else "[all]"}'
                 f'from {gps_start} to {gps_end}.')
        return self.triggers[i_start:i_end]
