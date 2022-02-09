

class Segment:

    def __init__(self, channel, x, f_sample, gps_time, duration, unit=None):
        self.channel = channel
        self.x = x
        self.f_sample = f_sample
        self.gps_time = gps_time
        self.duration = duration
        self.unit = unit
        self.decimated = False
