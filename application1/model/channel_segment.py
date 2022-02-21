from .channel import Channel


class ChannelSegment:

    def __init__(self, channel: Channel, data, gps_time):
        self.channel = channel
        self.data = data
        self.gps_start = gps_time
        self.n_points = len(self.data)
        self.duration = int(self.n_points / self.channel.f_sample)  # duration in seconds
        self.gps_end = gps_time + self.duration
        self.decimated = False
