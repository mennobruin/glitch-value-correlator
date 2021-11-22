import yaml
import logging
import sys


class ConfigurationManager:

    def __init__(self, path):
        self.path = path
        self.config = None
        self.LOG = self.get_logger(__name__)

    @staticmethod
    def get_logger(name) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s  - %(name)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def load_config(self):

        try:
            with open(self.path, 'r') as f:
                self.config = yaml.safe_load(f)
                return self.config
        except IOError as e:
            self.LOG.error(f"No configuration found at location {self.path}")
            raise e
