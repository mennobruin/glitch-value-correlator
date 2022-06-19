import webbrowser
import os
import bs4

from resources.constants import *


class HTMLReport:

    TEMP_FILE = RESOURCE_DIR + 'report/temp.html'

    def __init__(self, filename=REPORT_INDEX):
        self.filename = filename
        with open(REPORT_INDEX) as f:
            self.html = bs4.BeautifulSoup(f.read(), features='lxml')

    def __repr__(self):
        return self.html.prettify()

    def run_html(self):
        self.update_html()
        webbrowser.open('file://' + os.path.realpath(self.TEMP_FILE))

    def update_html(self):
        with open(self.TEMP_FILE, 'w+') as f:
            f.write(str(self.html.prettify()))

    def add_tag(self, tag_type, tag_id, parent_div=None):
        if parent_div:
            parent = self.html.find('div', id=parent_div)
        else:
            parent = self.html.find('body')
        new_tag = self.html.new_tag(tag_type, id=tag_id)
        parent.append(new_tag)

    def add_row_to_table(self, content: list, tag='td', table_id=None):
        table = self.html.find('table', id=table_id)

        row = self.html.new_tag('tr')
        for val in content:
            new_tag = self.html.new_tag(tag)
            new_tag.string = str(val)
            row.append(new_tag)

        table.append(row)

    def add_image(self, img, div_id=None):
        div = self.html.find('div', id=div_id)
        new_img = self.html.new_tag('img', src=PLOT_DIR + img)
        new_img['width'] = 450
        new_img['height'] = 360
        div.append(new_img)


if __name__ == '__main__':
    HTMLReport().run_html()
