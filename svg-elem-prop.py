'''This script remove SVGTestCase tag from .svg files'''

import os
import re

def remove_svg_elements():
    file_path = os.path.abspath('D:/SVG_test/cohtml-html/svg/')

    for file in os.listdir(file_path):
        print(file)
        text = ''
        for format in ['utf-8', 'utf-16', 'latin-1']:
            try:
                text = open(os.path.join(file_path, file), encoding=format).read()
                break
            except Exception as e:
                print(e)
                continue
        match = re.search(r'<SVGTestCase[\s\S]*>[\s\S]*</SVGTestCase>', text)
        if match:
            print("Matched with group")
        else:
            print("No match")

        remove_text = re.sub(r'<SVGTestCase[\s\S]*>[\s\S]*</SVGTestCase>', r' ', text, flags=re.M)
        with open(os.path.join(file_path, file), 'w', encoding='UTF-8') as f:
            f.write(remove_text)

remove_svg_elements()
