

class Segment:

    def __init__(self, channel, x, f_sample, gps_time, unit=None):
        self.channel = channel
        self.x = x
        self.f_sample = f_sample
        self.gps_time = gps_time
        self.unit = unit
