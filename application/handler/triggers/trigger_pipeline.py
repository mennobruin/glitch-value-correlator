"""
    Parent class for the local and Omicron trigger pipelines.
"""


class TriggerPipeline:

    OMICRON = 'omicron'
    LOCAL = 'local'

    def __init__(self):
        self.channel = None
        self.labels = None

    def get_segment(self, gps_start, gps_end):
        pass
