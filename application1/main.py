from core.auth.auth_service import AuthenticationService

from gwpy.timeseries import TimeSeries
from gwpy.detector.channel import ChannelList, Channel


def main(channel, t_start, t_stop):
    AuthenticationService()  # .authenticate([channel], t_start)
    c = Channel.query(channel)

    print(c)


if __name__ == '__main__':
    main(channel='H1:GDS-CALIB_STRAIN',
         t_start=1126259446,
         t_stop=1126259450)
