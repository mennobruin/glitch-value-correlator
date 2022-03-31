import webbrowser
import os

from resources.constants import REPORT_INDEX


class HTMLReport:

    DEFAULT_INDEX = REPORT_INDEX

    def __init__(self):
        pass

    @staticmethod
    def run_html(filename=REPORT_INDEX):
        webbrowser.open('file://' + os.path.realpath(filename))

    def generate_report(self):
        pass


if __name__ == '__main__':
    run_html()
