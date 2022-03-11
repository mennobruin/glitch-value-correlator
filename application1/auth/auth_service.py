import pathlib

from gwpy.detector import Channel
from gwpy.io import kerberos, nds2

from application1.config import config_manager

LOG = config_manager.get_logger(__name__)


class AuthenticationService:
    KERBEROS_CONFIG = "kerberos.{}"
    USERNAME = "username"
    KEYTAB = "keytab"

    def __init__(self):
        self._path = str(pathlib.Path(__file__).parents[1].resolve()) + "/resources/"
        self.config = ConfigurationManager().load_config()
        self._user = self.config[self.KERBEROS_CONFIG.format(self.USERNAME)]

        try:
            kerberos.kinit(username=self._user,
                           keytab=self._path + self._user + self.config[self.KERBEROS_CONFIG.format(self.KEYTAB)])
            LOG.info("Succesfully generated kerberos login ticket.")
        except Exception as e:
            LOG.error("Exception caught while running kinit:\n", e)

    def authenticate_nds2(self, channels: [Channel], start_time):
        for host, port in self._get_hosts(channels, start_time):
            try:
                connection = nds2.connect(host, port)
                LOG.info("Succesfully established nds2 connection.")
                return connection
            except (ValueError, RuntimeError) as e:
                LOG.warning(f"Exception caught while trying to connect to {host}:{port} \n {e}")
        LOG.error("Unable to establish nds2 connection, all attempts failed.")

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
    auth_service.authenticate_nds2(channels=["H1:GDS-CALIB_STRAIN"], start_time=1126259446)
