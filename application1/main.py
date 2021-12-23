from core.config import ConfigurationManager
from handler.data import Decimator, DataReader

LOG = ConfigurationManager.get_logger(__name__)


def main(t_start, t_stop, channel=None):
    reader = DataReader()
    decimator = Decimator()

    data = reader.get(channel, t_start, t_stop, source='raw_O3b_arch')
    # data_50hz = decimator.decimate(data, target_frequency=50)
    print(data.shape)


if __name__ == '__main__':
    main(channel='V1:Hrec_hoft_2_200Hz',
         t_start=1262228600,
         t_stop=1262228700)
