import logging
import pathlib

from gwpy.io import kerberos

from core.config.configuration_manager import ConfigurationManager

LOG = logging.getLogger(__name__)


class AuthenticationService:
    KERBEROS_CONFIG = "kerberos.{}"
    USERNAME = "username"
    KEYTAB = "keytab"

    def __init__(self):
        self._path = str(pathlib.Path(__file__).parents[1].resolve()) + "/resources/"
        self.config = ConfigurationManager(self._path + "config.yaml").load_config()
        self._user = self.config[self.KERBEROS_CONFIG.format(self.USERNAME)]

    def authenticate(self):
        kerberos.kinit(username=self._user,
                       keytab=self._path + self._user + self.config[self.KERBEROS_CONFIG.format(self.KEYTAB)])


if __name__ == '__main__':
    auth_service = AuthenticationService()
    auth_service.authenticate()