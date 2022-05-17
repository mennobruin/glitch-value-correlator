import numpy as np
from subprocess import Popen, PIPE


class Omicron:

    COMMAND = '/virgoApp/Omicron/v2r3p11/Linux-x86_64-CL7/omicron-print.exe channel={0} gps-start={1:d} gps-end={2:d}'
    FORMAT = [('gps', float), ('freq', float), ('snr', float)]

    def __init__(self, channel):
        self.channel = channel

    def get_segment(self, gps_start, gps_end):
        command = self.COMMAND.format(self.channel, gps_start, gps_end)
        process = Popen(command, stdout=PIPE, shell=True)
        triggers = np.loadtxt(process.stdout, dtype=self.FORMAT)
        triggers = triggers.view(dtype=(np.record, triggers.dtype), type=np.recarray)
        print(triggers)
        triggers.sort(order='gps')
        print(triggers)
        return triggers

