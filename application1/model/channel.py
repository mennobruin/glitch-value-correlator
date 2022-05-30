

class Channel:

    def __init__(self, name, f_sample, unit=None):
        self.name = name
        self.f_sample = f_sample
        self.unit = unit

    def __repr__(self):
        return self.name

    def __iter__(self):
        for value in vars(self).values():
            yield value


class ChannelSegment:

    def __init__(self, channel: Channel, data, gps_time):
        self.channel = channel
        self.data = data
        self.gps_start = gps_time
        self.n_points = len(self.data)
        self.duration = int(self.n_points / self.channel.f_sample)  # duration in seconds
        self.gps_end = gps_time + self.duration
        self.resampled = False
