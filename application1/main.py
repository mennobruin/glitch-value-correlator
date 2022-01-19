import matplotlib.pyplot as plt

from application1.model import Segment, Hist
from application1.handler.data import Decimator, DataReader
from core.config import ConfigurationManager

LOG = ConfigurationManager.get_logger(__name__)


def main(source, channel_name, t_start, t_stop):
    reader = DataReader()
    decimator = Decimator()

    bl_patterns = ['*max', '*min', 'V1:VAC*', 'V1:Daq*', '*rms']
    available_channels = reader.get_available_channels(source, t_start, patterns=bl_patterns)
    print(len(available_channels))

    segment: Segment = reader.get(channel_name, t_start, t_stop, source=source)
    segment_50hz: Segment = decimator.decimate(segment, target_frequency=50)

    h = Hist(segment_50hz)
    plt.bar(h.xgrid, h.counts, width=h.span / h.nbin)
    plt.xlim([h.offset, h.offset + h.span])
    plt.show()


if __name__ == '__main__':
    main(source='/virgoData/ffl/raw_O3b_arch',
         channel_name='V1:Hrec_hoft_2_200Hz',
         t_start=1262228600,
         t_stop=1262228700)
