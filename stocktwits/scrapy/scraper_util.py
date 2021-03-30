from selenium import webdriver
import os

CHROME_DRIVER_PATH = '/usr/bin/chromedriver'

def get_chrome_options():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-usage')
    return options

def get_web_driver():
    if(os.path.exists(CHROME_DRIVER_PATH)):
        options = get_chrome_options()
        return webdriver.Chrome(
                executable_path = CHROME_DRIVER_PATH,
                options = options)
    else:
        return None

