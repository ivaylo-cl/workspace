'''This script makes screenshots from chrome. Display resolution should be 3840x2150 with setting size 150%'''

from selenium import webdriver
import os
import time

driver = webdriver.Chrome()
# driver.maximize_window()
driver.set_window_size(547, 531)

def loadTest():
    svgPath = 'D:/SVG_test/cohtml-html/svg/'

    for entry in os.listdir(svgPath):
        if os.path.isfile(os.path.join(svgPath, entry)):
            driver.get(svgPath + entry)
            driver.save_screenshot('D:/Work/PyTests/screenshots/' + entry[:-4] + '-expected.png')
            print(entry)
            time.sleep(1)
    driver.close()

loadTest()