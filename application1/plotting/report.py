import webbrowser
import os
import bs4
import base64

from resources.constants import REPORT_INDEX


class HTMLReport:

    TEMP_FILE = 'resources/report/temp.html'

    def __init__(self, filename=REPORT_INDEX):
        self.filename = filename
        with open(REPORT_INDEX) as f:
            self.html = bs4.BeautifulSoup(f.read(), features='lxml')

    def run_html(self):
        print(self.html.prettify())
        webbrowser.open('file://' + os.path.realpath(self.TEMP_FILE))

    def update_html(self):
        with open(self.TEMP_FILE, 'w+') as f:
            f.write(str(self.html.prettify()))

    def add_row_to_table(self, content: list, tag='td', table_class=None):
        table = self.html.find('table', class_=table_class)

        row = self.html.new_tag('tr')
        for val in content:
            new_tag = self.html.new_tag(tag)
            new_tag.string = str(val)
            row.append(new_tag)

        table.append(row)

    def generate_report(self):
        pass


if __name__ == '__main__':
    HTMLReport().run_html()
