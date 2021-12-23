from core.config import ConfigurationManager
from handler.data import Decimator, DataReader
from model.channel import Channel

LOG = ConfigurationManager.get_logger(__name__)


def main(t_start, t_stop, channel_name=None):
    reader = DataReader()
    decimator = Decimator()

    channel: Channel = reader.get(channel_name, t_start, t_stop, source='raw_O3b_arch')
    data_50hz = decimator.decimate(channel.x, input_frequency=channel.dx, target_frequency=50)
    print(channel.x.shape)
    print(data_50hz.shape)


if __name__ == '__main__':
    main(channel_name='V1:Hrec_hoft_2_200Hz',
         t_start=1262228600,
         t_stop=1262228700)
