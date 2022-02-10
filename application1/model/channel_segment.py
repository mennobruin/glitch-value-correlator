

class ChannelSegment:

    def __init__(self, channel, data, f_sample, gps_time, duration, unit=None):
        self.channel = channel
        self.data = data
        self.f_sample = f_sample
        self.gps_start = gps_time
        self.gps_end = gps_time + duration
        self.duration = duration
        self.unit = unit
        self.decimated = False
