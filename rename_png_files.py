import os

def rename_files():
    path = 'D:/SVG_test/cohtml-html/png'

    for filename in os.listdir(path):
            old_file = os.path.join(path, filename)
            new_file = os.path.join(path, filename[:-4:] + '-expected' + '.png')
            os.rename(old_file, new_file)

rename_files()