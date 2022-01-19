from fnmatch import fnmatch

from application1.model.segment import Segment
from application1.handler.data import Decimator, DataReader
from core.config import ConfigurationManager

LOG = ConfigurationManager.get_logger(__name__)


def main(source, channel_name, t_start, t_stop):
    reader = DataReader()
    decimator = Decimator()

    # available_channels = reader.get_available_channels(source, t_start)

    segment: Segment = reader.get(channel_name, t_start, t_stop, source=source)
    print(segment.x.size)
    print(segment.f_sample)
    print(segment.gps_time)
    print(segment.channel)
    print(segment.decimated)
    segment_50hz: Segment = decimator.decimate(segment, target_frequency=50)
    print(segment_50hz.x.size)
    print(segment_50hz.f_sample)
    print(segment_50hz.gps_time)
    print(segment_50hz.channel)
    print(segment_50hz.decimated)


if __name__ == '__main__':
    main(source='/virgoData/ffl/raw_O3b_arch',
         channel_name='V1:Hrec_hoft_2_200Hz',
         t_start=1262228600,
         t_stop=1262228700)
