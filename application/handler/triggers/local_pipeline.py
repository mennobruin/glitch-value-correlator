import numpy as np

from .trigger_pipeline import TriggerPipeline
from application.handler.data.reader.csv import CSVReader
from application.config import config_manager

LOG = config_manager.get_logger(__name__)


class LocalPipeline(TriggerPipeline):

    NAME = 'local'
    GPS_TIME = 'GPStime'
    LABEL = 'label'

    def __init__(self, trigger_file, trigger_type=None):
        super(LocalPipeline, self).__init__()
        self.reader = CSVReader()
        self.trigger_type = trigger_type
        self.triggers = self._load_triggers(trigger_file)

    def _load_triggers(self, path_to_csv):
        triggers = self.reader.load_csv(path_to_csv, usecols=[self.GPS_TIME, self.LABEL])
        if self.trigger_type:
            triggers = triggers.loc[triggers[self.LABEL] == self.trigger_type]
            self.labels = [self.trigger_type]
        else:
            self.labels = set(triggers[self.LABEL].values)
        sorted_triggers = triggers.sort_values(self.GPS_TIME)
        return sorted_triggers

    def get_segment(self, gps_start, gps_end):
        i_start, i_end = np.searchsorted(self.triggers[self.GPS_TIME], (gps_start, gps_end))
        LOG.info(f'Found {i_end - i_start} triggers of type {self.trigger_type if self.trigger_type else "[all]"} '
                 f'from {gps_start} to {gps_end}.')
        return self.triggers[i_start:i_end]
