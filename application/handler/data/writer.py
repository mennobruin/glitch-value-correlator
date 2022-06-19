import csv
import os

from resources.constants import RESOURCE_DIR
from application1.utils import check_extension, create_dir_if_not_exists
from application1.config import config_manager

LOG = config_manager.get_logger(__name__)


class DataWriter:

    def __init__(self):
        self.default_path = RESOURCE_DIR

    def write_csv(self, data, file_name, file_path=None):
        if not file_path:
            file_path = self.default_path
        else:
            create_dir_if_not_exists(file_path)

        if os.path.isfile(file_path + file_name):
            LOG.warning(f'Overwriting existing {file_name}.')
        file_name = check_extension(file_name, extension='.csv')

        with open(file_path + file_name, 'w+') as f:
            writer = csv.writer(f)
            for obj in data:
                writer.writerow(obj)
