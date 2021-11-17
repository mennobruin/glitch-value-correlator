import yaml
import logging

LOG = logging.getLogger(__name__)


class ConfigurationManager:

    def __init__(self, path):
        self.path = path

    def load(self):
        try:
            with open(self.path, 'r') as f:
                return yaml.safe_load(f)
        except IOError as e:
            LOG.error(f"No configuration found at location {self.path} \n {e}")
