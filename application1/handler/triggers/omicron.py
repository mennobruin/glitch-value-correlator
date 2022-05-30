import os

import numpy as np
from subprocess import Popen, PIPE

from application1.utils import exit_on_error
from application1.config import config_manager

LOG = config_manager.get_logger(__name__)


class Omicron:

    COMMAND = 'omicron-print channel={0} gps-start={1:d} gps-end={2:d}'
    FORMAT = [('gps', float), ('freq', float), ('snr', float)]

    def __init__(self, channel):
        self.channel = channel

    def get_segment(self, gps_start, gps_end):
        command = self.COMMAND.format(self.channel.name, gps_start, gps_end)
        process = Popen(command, stdout=PIPE, shell=True)
        data = process.stdout

        print(type(data.readline()), data.readline())
        if data.readline():
            triggers = np.loadtxt(data, dtype=self.FORMAT)
            triggers = triggers.view(dtype=(np.record, triggers.dtype), type=np.recarray)
            print(triggers.shape)
            print(triggers)
            triggers.sort(order='gps')
            return triggers
        else:
            LOG.error(f"No triggers found / failed to load triggers between {gps_start} and {gps_end}. "
                      f"Are you in the correct environment? Try 'source /virgoDev/Omicron/vXrYpZ/cmt/setup.sh' first.")
            exit_on_error()
