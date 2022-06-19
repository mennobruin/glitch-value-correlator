

class BaseFOM:

    def __init__(self):
        self.table = None

    def rank(self):
        self.table.sort(order='fom')
