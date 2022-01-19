from model.channel import Channel
from handler.data import Decimator, DataReader
from .core.config import ConfigurationManager

LOG = ConfigurationManager.get_logger(__name__)


def main(channel_name, t_start, t_stop):
    reader = DataReader()
    decimator = Decimator()

    available_channels = reader.get_available_channels(channel_name, t_start)
    print(available_channels)

    # channel1: Channel = reader.get(channel_name, t_start, t_stop, source='raw_O3b_arch')
    # channel2: Channel = reader.get(channel_name, t_start, t_stop, source='raw_O3b_arch')
    # data1_50hz = decimator.decimate(channel1.x, input_frequency=channel1.dx, target_frequency=50)
    # data2_50hz = decimator.decimate(channel2.x, input_frequency=channel2.dx, target_frequency=50)



if __name__ == '__main__':
    main(channel_name='V1:Hrec_hoft_2_200Hz',
         t_start=1262228600,
         t_stop=1262228700)
