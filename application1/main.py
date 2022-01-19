from fnmatch import fnmatch

from application1.model.channel import Channel
from application1.handler.data import Decimator, DataReader
from core.config import ConfigurationManager

LOG = ConfigurationManager.get_logger(__name__)


def main(source, channel_name, t_start, t_stop):
    reader = DataReader()
    decimator = Decimator()

    # available_channels = reader.get_available_channels(source, t_start)

    channel1: Channel = reader.get(channel_name, t_start, t_stop, source=source)
    data1_50hz = decimator.decimate(channel1.x, input_frequency=channel1.dx, target_frequency=50)
    
    print(channel1.gps_time)
    print(channel1.dx)
    print(len(channel1.x))


if __name__ == '__main__':
    main(source='/virgoData/ffl/raw_O3b_arch',
         channel_name='V1:Hrec_hoft_2_200Hz',
         t_start=1262228600,
         t_stop=1262228700)
