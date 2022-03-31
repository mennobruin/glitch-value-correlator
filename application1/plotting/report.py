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

        for val in content:
            new_tag = self.html.new_tag(tag)
            new_tag.append(val)
            table.append(new_tag)

    def generate_report(self):
        pass


if __name__ == '__main__':
    HTMLReport().run_html()
