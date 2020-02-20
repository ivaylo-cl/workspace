'''This script create html files'''

import os

svg = os.listdir('D:/SVG_test/cohtml-html/svg')

for i in svg:

    basefile = 'D:/SVG_test/cohtml-html/html'
    entry = i.replace('.svg', '.html')
    file = open(os.path.join(basefile, entry), 'w')
    html = ['<html>\n\n\t', '<style>\n\t\t', 'body {\n\t\t\t'
            'background-color: transparent;\n\t\t\t', 'margin: 0px;\n\t\t',
            '}\n\n\t\t', '#main {\n\t\t\t', 'background-color: transparent;\n\t\t\t',
            'width:800px;\n\t\t\t', 'height:600px;\n\t\t','}\n\n\t', '</style>\n\n\t', '<body>\n\n\t\t'
            '<img id="main" src= "../cohtml-html/svg/' + str(i) + '"' + ' />\n\n\t', '</body>\n\n', '</html>']
    file.writelines(html)
    file.close()