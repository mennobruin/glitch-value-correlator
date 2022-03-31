import webbrowser
import os
import bs4

from resources.constants import REPORT_INDEX


class HTMLReport:

    def __init__(self, filename=REPORT_INDEX):
        self.filename = filename
        with open(REPORT_INDEX) as f:
            self.html = bs4.BeautifulSoup(f.read())

    def run_html(self):
        self.update_html()
        webbrowser.open('file://' + os.path.realpath(self.filename))

    def update_html(self):
        with open(REPORT_INDEX, 'w') as f:
            f.write(str(self.html))

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
