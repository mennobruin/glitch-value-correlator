import logging
import pathlib

from gwpy.io import nds2, kerberos
from gwpy.detector import Channel

from core.config.configuration_manager import ConfigurationManager

LOG = logging.getLogger(__name__)
config_manager = ConfigurationManager("..\\resources\\config.yaml")


class AuthenticationService:
    KERBEROS_CONFIG = "kerberos.{}"
    USERNAME = "username"
    KEYTAB = "keytab"

    def __init__(self):
        self.config = config_manager.load()
        self._user = self.config[self.KERBEROS_CONFIG.format(self.USERNAME)]
        self._path = str(pathlib.Path(__file__).parents[1].resolve()) + "\\resources\\"

        kerberos.kinit(username=self._user,
                       keytab=self._path + self._user + self.config[self.KERBEROS_CONFIG.format(self.KEYTAB)])

    def authenticate(self, channels: [Channel], start_time):

        for host, port in self._get_hosts(channels, start_time):
            try:
                nds2.connect(host, port)
            except (ValueError, RuntimeError) as e:
                LOG.warning(f"Exception caught while trying to connect to {host}:{port} \n {e}")

    @staticmethod
    def _get_hosts(channels: [Channel], start_time):
        ifos = set([Channel(channel).ifo for channel in channels])

        if len(ifos) == 1:
            ifo = list(ifos)[0]
        else:
            ifo = None

        return nds2.host_resolution_order(ifo, epoch=start_time)


if __name__ == '__main__':
    auth_service = AuthenticationService()
    auth_service.authenticate(channels=["H1:GDS-CALIB_STRAIN"], start_time=1126259446)
