import csv
import sys
import re

maxInt = sys.maxsize

while True:
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)


def get_png_name():
    test_result = re.compile('\\\([\w\-]+?-t).png')
    with open('index.html', 'r') as html_file:
        for result in html_file:
            strip = result.strip()
            match = test_result.search(strip)

            if match:
                png_name = match.group(1)
                print(png_name)
                return png_name


def CreateCsvFile():
    for format in ['utf-8', 'utf-16']:
        try:
            with open('SVG-Log-2020-01-21 13-06-18.txt', 'r', encoding=format) as in_file:
                with open('SVG-Log-2020-01-21 13-06-18.csv', 'w', encoding=format, newline='') as out_file:
                    with open('index.html', 'r+', encoding=format) as file:
                        filedata = file.read()
                        file.seek(0)

                        current_html_test_name = ''
                        csv_warnings = []
                        fieldnames = ['Tests', 'Pass/Fail', 'Missing Features/Bugs', 'Note']
                        writer = csv.DictWriter(out_file, fieldnames=fieldnames)
                        writer.writeheader()

                        lines = in_file.readlines()
                        current_html_test_name = lines[0].strip()

                        for line in lines:
                            stripped_line = line.strip()
                            png_name = ''

                            if 'Warning' in line:
                                csv_warnings.append(line)

                            elif 'color' in line:
                                csv_warnings.append(line)

                            elif 'element' in line:
                                csv_warnings.append(line)

                            elif 'if(' in line:
                                csv_warnings.append(line)

                            if '.html' in line:
                                if current_html_test_name == stripped_line:
                                    continue

                                csv_warnings = list(set(csv_warnings))
                                writer.writerow({'Tests': current_html_test_name, 'Pass/Fail': '',
                                            'Missing Features/Bugs': '', 'Note': ''.join(csv_warnings)})
                                # print('Test name:' + current_html_test_name + '\n' + 'Warnings: ' + ''.join(csv_warnings))

                                png_name = current_html_test_name[:-4] + 'png'
                                print(png_name)

                                def sub_callback(match):
                                    to_return = match.group(1) + '</pre><textarea readonly rows="10" cols="120">' \
                                                + ''.join(csv_warnings) + '</textarea></pre><br>' + match.group(3)
                                    print(to_return)
                                    return to_return

                                pattern = re.compile('(<tr>[\s\S]*?' + png_name + '[\s\S]*?)'
                                                                            '(Max color mismatch 255)([\s\S]*?</tr>)')
                                filedata = re.sub(pattern, sub_callback, filedata)

                                csv_warnings = []
                                current_html_test_name = stripped_line
                        file.write(filedata)
                        file.truncate()
                        break
        except Exception as e:
            print(e)
            continue

CreateCsvFile()
