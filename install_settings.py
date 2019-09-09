import os
if (os.name=='posix'):
    PATH_INSTALLAZIONE_TESSERACT = ('/usr/local/bin/tesseract')
    CHROME = os.path.join('Applications', 'Google Chrome.app', 'Contents', 'MacOS', 'Google  Chrome')
else:
    PATH_INSTALLAZIONE_TESSERACT = r'E:\Tesseract-OCR\tesseract.exe'
    CHROME = os.path.join('C:\\', 'Program Files (x86)', 'Google', 'Chrome', 'Application', 'chrome.exe')
    WEBDRIVER_PATH = os.path.join('C:\\', 'Program Files (x86)', 'ChromeDriverForSelenium', 'chromedriver.exe')