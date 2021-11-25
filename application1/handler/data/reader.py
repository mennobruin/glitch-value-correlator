import pandas as pd
import pathlib
import os

from core.config.configuration_manager import ConfigurationManager

LOG = ConfigurationManager.get_logger(__name__)


class DataReader:
    def __init__(self):
        self.default_path = str(pathlib.Path(__file__).parents[2].resolve()) + "\\resources\\"

    def load_csv(self, csv_file) -> pd.DataFrame:
        LOG.info(f"Loading {csv_file}")
        if not os.path.isfile(csv_file):
            csv_file = self.default_path + 'csv\\' + csv_file
        else:
            LOG.error(f"Unable to load csv_file: {csv_file} \n Check if the file exists.")
            raise FileNotFoundError

        with open(csv_file, 'r') as f:
            return pd.read_csv(f)
