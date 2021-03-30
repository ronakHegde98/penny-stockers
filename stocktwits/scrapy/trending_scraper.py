from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
from util import get_current_datetime

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-usage')

website = 'https://stocktwits.com/rankings/watchers'

wd = webdriver.Chrome(executable_path='/usr/bin/chromedriver', options=options)
wd.get(website)
html = wd.page_source

tables = pd.read_html(html)
df = tables[0]

print(df)

symbols = df['Symbol']

print(get_current_datetime())
print(df.iloc[0])
print(set(zip(list(df['Symbol']),list(df['Price']))))

print(df[['Symbol', 'Price', 'Count']])

wd.close()
