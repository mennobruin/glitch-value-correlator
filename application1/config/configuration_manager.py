import yaml
import logging
import sys
import os

from datetime import datetime

from resources.constants import RESOURCE_DIR


class ConfigurationManager:

    CONFIG_PATH = RESOURCE_DIR + 'config.yaml'
    LOG_DIRECTORY = RESOURCE_DIR + 'logs/'

    def __init__(self):
        os.makedirs(self.LOG_DIRECTORY, exist_ok=True)
        self.LOG = self.get_logger(__name__)

    def get_logger(self, name) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s  - %(name)s - %(message)s')

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.INFO)
        stdout_handler.setFormatter(formatter)

        file_handler = logging.FileHandler(self.LOG_DIRECTORY + '{:%Y-%m-%d}.log'.format(datetime.now()))
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        logger.addHandler(stdout_handler)
        logger.addHandler(file_handler)

        return logger

    def load_config(self):
        try:
            with open(self.CONFIG_PATH, 'r') as f:
                return yaml.safe_load(f)
        except IOError as e:
            self.LOG.error(f"No configuration found at location {self.CONFIG_PATH}")
            raise e
