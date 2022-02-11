

class Channel:

    def __init__(self, name, f_sample, unit=None):
        self.name = name
        self.f_sample = f_sample
        self.unit = unit

    def __str__(self):
        return f'{self.name}, {self.f_sample}, {self.unit}'
