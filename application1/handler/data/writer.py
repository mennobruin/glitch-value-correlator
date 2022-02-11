import csv

from application1.utils import *

LOG = ConfigurationManager.get_logger(__name__)


class Writer:

    def __init__(self):
        self.default_path = get_resource_path(depth=2)

    def write_csv(self, data, file_name, file_path=None):
        file_path = file_path if file_path else self.default_path
        file_name = check_extension(file_name, extension='.csv')

        with open(file_path + file_name, 'w+') as f:
            writer = csv.writer(f)
            writer.writerows(data)
