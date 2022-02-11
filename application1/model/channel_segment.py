from .channel import Channel


class ChannelSegment:

    def __init__(self, channel: Channel, data, gps_time, duration):
        self.channel = channel
        self.data = data
        self.gps_start = gps_time
        self.gps_end = gps_time + duration
        self.duration = duration
        self.decimated = False
