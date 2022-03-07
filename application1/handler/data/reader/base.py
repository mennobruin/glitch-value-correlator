import os
from application1.utils import get_resource_path
from core.config.configuration_manager import ConfigurationManager

LOG = ConfigurationManager.get_logger(__name__)


class BaseReader:

    def __init__(self):
        self.default_path = get_resource_path(depth=2)

    def _check_path_exists(self, file_loc, file):
        LOG.info(f"Loading {file}")
        if not os.path.isfile(file):
            csv_file = self.default_path + file_loc + file
            if not os.path.isfile(csv_file):
                LOG.error(f"Unable to load file: {file}, check if the file exists.")
                raise FileNotFoundError




