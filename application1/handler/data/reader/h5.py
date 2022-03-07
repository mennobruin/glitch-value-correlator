import h5py

from .base import BaseReader

from application1.utils import check_extension


class H5Reader(BaseReader):

    H5_DIR = 'ds_data/data/'

    def __init__(self):
        super(H5Reader, self).__init__()
        self.h5_file = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.h5_file.close()

    def load_h5(self, h5_file):
        h5_file = check_extension(h5_file, extension='.h5')
        self._check_path_exists(file_loc=self.H5_DIR, file=h5_file)

        file = h5py.File(h5_file, 'r')


