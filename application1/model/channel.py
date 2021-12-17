

class Channel:

    def __init__(self, x, dx, gps_time):
        print("creating channel")
        print(dx, gps_time)
        self.x = x
        self.dx = dx
        self.gps_time = gps_time
