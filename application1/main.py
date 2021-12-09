import time

from gwpy.timeseries import TimeSeries
from virgotools.frame_lib import getChannel

from core.config.configuration_manager import ConfigurationManager
from handler.data.decimator import Decimator

LOG = ConfigurationManager.get_logger(__name__)


def get_data(channel, t_start, t_stop, connection=None, verbose=False):
    LOG.info(f"Fetching data from {channel}...")
    t0 = time.time()
    if connection:
        data = TimeSeries.fetch(channel, t_start, t_stop, connection=connection, verbose=verbose)
    else:
        data = getChannel(channel, t_start, t_stop).data
    LOG.info(f"Fetched data from {channel}, time elapsed: {time.time() - t0:.1f}s")
    return data


def main(t_start, t_stop, channel=None):

    data = get_data(channel, t_start, t_stop)
    decimator = Decimator()
    data_50hz = decimator.decimate(data, target_frequency=50)


if __name__ == '__main__':
    main(channel='V1:INJ_IMC_TRA_DC',
         t_start=1171432800,
         t_stop=1171450800)
