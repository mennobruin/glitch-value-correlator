import pandas as pd

from .base import BaseReader
from application1.utils import check_extension


class CSVReader(BaseReader):

    CSV_DIR = 'csv/'

    def __init__(self):
        super(CSVReader, self).__init__()

    def load_csv(self, csv_file, usecols=None, header=None) -> pd.DataFrame:
        csv_file = check_extension(csv_file, extension='.csv')
        csv_file = self._check_path_exists(file_loc=self.CSV_DIR, file=csv_file)
        return pd.read_csv(csv_file, usecols=usecols, header=header)
