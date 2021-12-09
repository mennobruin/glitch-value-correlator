import time

import matplotlib.pyplot as plt

from gwpy.timeseries import TimeSeries
from gwpy.detector.channel import ChannelList, Channel

from handler.data.reader import DataReader
from core.auth.auth_service import AuthenticationService
from core.config.configuration_manager import ConfigurationManager

LOG = ConfigurationManager.get_logger(__name__)


def get_data(channel, t_start, t_stop, connection=None, verbose=False, frametype='raw'):
    LOG.info(f"Fetching data from {channel}...")
    t0 = time.time()
    if connection:
        data = TimeSeries.fetch(channel, t_start, t_stop, connection=connection, verbose=verbose)
    else:
        data = TimeSeries.get(channel, t_start, t_stop, allow_tape=True, verbose=verbose, frametype=frametype)
    LOG.info(f"Fetched data from {channel}, time elapsed: {time.time() - t0:.1f}s")
    return data


def main(t_start, t_stop, channel=None):
    reader = DataReader()
    file_name = 'gspy_O3b_c090_blip.csv'
    df = reader.load_csv(file_name)

    gps_time = df["GPStime"].values[0]
    duration = df["duration"].values[0]
    print(gps_time)

    data = get_data(channel, t_start=gps_time-duration/2, t_stop=gps_time+duration/2, frametype='trend')
    plt.plot(range(len(data)), data, 'b-')
    plt.show()


if __name__ == '__main__':
    main(channel='V1:INJ_IMC_TRA_DC',
         t_start=1171432800,
         t_stop=1171450800)