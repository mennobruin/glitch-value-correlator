

class Channel:

    def __init__(self, x, dx, gps_time, unit=None):
        print("creating channel")
        print(dx, gps_time)
        self.x = x
        self.dx = dx
        self.unit = unit
        self.gps_time = gps_time
