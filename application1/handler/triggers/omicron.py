import os

import numpy as np
from subprocess import Popen, PIPE

from application1.model.channel import Channel
from application1.utils import exit_on_error
from application1.config import config_manager

LOG = config_manager.get_logger(__name__)


class Omicron:

    COMMAND = 'omicron-print channel={0} gps-start={1:d} gps-end={2:d}'
    FORMAT = [('gps', float), ('freq', float), ('snr', float)]

    def __init__(self, channel):
        self.channel = channel
        self.labels = {'omicron'}

    def get_segment(self, gps_start, gps_end):
        LOG.info(f"Loading Omicron triggers from {gps_start} to {gps_end}...")
        command = self.COMMAND.format(self.channel, gps_start, gps_end)
        process = Popen(command, stdout=PIPE, shell=True)
        data = process.stdout
        if data.readline():
            triggers = np.loadtxt(data, dtype=self.FORMAT)
            triggers = triggers.view(dtype=(np.record, triggers.dtype), type=np.recarray)
            triggers.sort(order='gps')
            return triggers.gps
        else:
            LOG.error(f"No triggers found / failed to load triggers between {gps_start} and {gps_end}. "
                      f"Are you in the correct environment? Try 'source /virgoDev/Omicron/vXrYpZ/cmt/setup.sh' first.")
            exit_on_error()


if __name__ == '__main__':
    pipeline = Omicron(channel="V1:ENV_WEB_MAG_N")
    pipeline.get_segment(gps_start=1262678418, gps_end=1262908818)
