import os

import numpy as np
from subprocess import Popen, PIPE

from .trigger_pipeline import TriggerPipeline
from application.model.channel import Channel
from application.utils import exit_on_error
from application.config import config_manager

LOG = config_manager.get_logger(__name__)


class Omicron(TriggerPipeline):

    NAME = 'omicron'
    COMMAND = 'omicron-print channel={0} gps-start={1:d} gps-end={2:d}'
    FORMAT = [('gps', float), ('freq', float), ('snr', float)]

    def __init__(self, channel, snr_threshold=None):
        super(Omicron, self).__init__()
        self.channel = channel
        self.snr_threshold = snr_threshold
        self.labels = {self.NAME}

    def get_segment(self, gps_start, gps_end):
        LOG.info(f"Loading Omicron triggers from {gps_start} to {gps_end}...")
        command = self.COMMAND.format(self.channel, gps_start, gps_end)
        process = Popen(command, stdout=PIPE, shell=True)
        data = process.stdout
        if data.readline():
            triggers = np.loadtxt(data, dtype=self.FORMAT)
            triggers = triggers.view(dtype=(np.record, triggers.dtype), type=np.recarray)
            if self.snr_threshold:
                triggers = triggers[triggers.snr > self.snr_threshold]
            triggers.sort(order='gps')
            LOG.info(f'Found {triggers.shape[0]} triggers.')
            return triggers.gps
        else:
            LOG.error(f"No triggers found / failed to load triggers between {gps_start} and {gps_end}. "
                      f"Are you in the correct environment? Try 'source /virgoDev/Omicron/vXrYpZ/cmt/setup.sh' first.")
            exit_on_error()


if __name__ == '__main__':
    pipeline = Omicron(channel="V1:ENV_WEB_MAG_N")
    pipeline.get_segment(gps_start=1262678418, gps_end=1262908818)
