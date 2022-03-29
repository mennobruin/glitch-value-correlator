import os
from resources.constants import RESOURCE_DIR

from application1.config import config_manager

LOG = config_manager.get_logger(__name__)


class BaseReader:

    def __init__(self):
        self.default_path = RESOURCE_DIR

    def _check_path_exists(self, file_loc, file):
        if not os.path.isfile(file):
            file = self.default_path + file_loc + file
            if not os.path.isfile(file):
                LOG.error(f"Unable to load file: {file}, check if the file exists.")
                raise FileNotFoundError
        return file
