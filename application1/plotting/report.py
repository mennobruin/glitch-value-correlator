import webbrowser
import os

from resources.constants import REPORT_INDEX


def run_html(filename=REPORT_INDEX):
    webbrowser.open('file://' + os.path.realpath(filename))


class HTMLReport:

    def __init__(self):
        pass

    def generate_report(self):
        pass


if __name__ == '__main__':
    print('1')
    run_html()
    print('2')
