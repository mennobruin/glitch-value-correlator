import csv
import os

from application1.utils import check_extension, RESOURCE_PATH
from core.config.configuration_manager import ConfigurationManager

LOG = ConfigurationManager.get_logger(__name__)


class DataWriter:

    def __init__(self):
        self.default_path = RESOURCE_PATH

    def write_csv(self, data, file_name, file_path=None):
        file_path = file_path if file_path else self.default_path
        if os.path.isfile(file_path + file_name):
            LOG.warning(f'Overwriting existing {file_name}.')
        file_name = check_extension(file_name, extension='.csv')

        with open(file_path + file_name, 'w+') as f:
            writer = csv.writer(f)
            for obj in data:
                writer.writerow(obj)
