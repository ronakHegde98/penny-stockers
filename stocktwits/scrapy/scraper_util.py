from selenium.common.exceptions import WebDriverException #type: ignore 
from selenium import webdriver #type: ignore
import pandas as pd # type: ignore
import os
import requests
from bs4 import BeautifulSoup # type: ignore

CHROME_DRIVER_PATH = '/usr/bin/chromedriver'

''' SELENIUM UTIL FUNCTIONS '''
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

def get_page_source(wd: webdriver, url: str) -> str:
    wd.get(url)
    return wd.page_source

def kill_chrome():
    os.system('pkill -9 -f chrome')


''' BEAUTIFULSOUP UTIL FUNCTIONS '''
def get_soup_object(url: str) -> BeautifulSoup:
    if(url):
        response = requests.get(url)
        if(response.status_code == 200):
            soup = BeautifulSoup(response.content, 'lxml')
            return soup

