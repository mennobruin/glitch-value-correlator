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

    def add_div(self, div_id, parent_class=None):
        if parent_class:
            parent_div = self.html.find('div', class_=parent_class)
        else:
            parent_div = self.html.find('body')
        new_div = self.html.new_tag('div', id=div_id)
        parent_div.append(new_div)

    def add_row_to_table(self, content: list, tag='td', table_class=None):
        table = self.html.find('table', class_=table_class)

        row = self.html.new_tag('tr')
        for val in content:
            new_tag = self.html.new_tag(tag)
            new_tag.string = str(val)
            row.append(new_tag)

        table.append(row)

    def add_image(self, img, div_class=None, div_id=None):
        print('test1')
        print(self.html.find_all('div', class_='images', id='rank_5'))
        print('test2')
        div = self.html.find('div', class_=div_class, id=div_id)
        new_img = self.html.new_tag('img', src=PLOT_DIR + img)
        new_img['width'] = 450
        new_img['height'] = 360
        div.append(new_img)


if __name__ == '__main__':
    HTMLReport().run_html()
