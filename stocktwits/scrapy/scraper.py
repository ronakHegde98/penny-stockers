from util import get_current_datetime, is_int
from scraper_util import get_web_driver
from sheets_util import fill_column,get_sheet, get_new_col_index, insert_timestamp_header, append_column, get_new_col_values

from bs4 import BeautifulSoup
from pathlib import Path
import pandas as pd
import requests
import random
import time
import gspread
import logging
import sys
import os

# adding stocktwits module to system path 
stocktwits_path = str(Path(os.getcwd()).parent) + '/'
sys.path.append(stocktwits_path)
from config.creds import get_gsheets_client 

class StockTwitsScraper:  

    BASE_URL = 'https://stocktwits.com'
    spreadsheet_name = 'Penny Stalkers'

    def __init__(self):
        gsheets_client = get_gsheets_client()
        self.spreadsheet = gsheets_client.open(self.spreadsheet_name)
    
    def get_symbol_price(self, soup):
        price_class = 'st_3zYaKAL'
        price_tag = soup.find('span', attrs = {'class': price_class})
        if(price_tag):
            return price_tag.text
        else:
            return '' 
   
    def get_symbol_watch_count(self, soup):
        watch_count_tag = soup.find('strong')
        if(watch_count_tag):
            return watch_count_tag.text
        else:
            return ''

class WatchCountScraper(StockTwitsScraper):
    def __init__(self):
        pass

class TrendingSymbolScraper(StockTwitsScraper):
    """ scraping the top ten symbols with most new watchers in the last 24 hours"""
   
    # TODO: create a script that gets the latest chromedriver and chrome version (every week once)
    # TODO: kill the process after it is spawned using try/except/finally

    PRICE_GSHEET = 'TrendingPrices'
    WATCH_COUNT_GSHEET = 'TrendingWatchCount'

    def __init__(self):
        super().__init__()
        scraping_category = 'watchers'
        self.TRENDING_URL = self.BASE_URL + f'/rankings/{scraping_category}'
        self.price_sheet = get_sheet(self.spreadsheet, self.PRICE_GSHEET)
        self.watch_sheet = get_sheet(self.spreadsheet, self.WATCH_COUNT_GSHEET)

    def get_trending_symbols(self, wd):
        #TODO: check if request was successful
        wd.get(self.TRENDING_URL)
    
        page_html = wd.page_source
        dataframes = pd.read_html(page_html)
        trending_df = dataframes[0]     
        symbols = list(trending_df['Symbol'])
        return symbols
    
    def scrape(self):
        pass

    def get_trending_symbol_info(self,ticker_url:str):
        """ return prices and counts of trending symbols """
        price, watch_count = '', ''

        if(ticker_url):
            r = requests.get(ticker_url)
            if(r.status_code == 200):
                soup = BeautifulSoup(r.content, 'lxml')
                price = self.get_symbol_price(soup)
                watch_count = self.get_symbol_watch_count(soup)

        return price, watch_count

    def execute(self):
        #TODO: kill any running instances of chrome before opening 
        wd = get_web_driver()
        trending_symbols_raw = self.get_trending_symbols(wd)
        wd.close()
        

        print(trending_symbols_raw)
        trending_symbols = [symbol.replace('-', '.') for symbol in trending_symbols_raw]
        new_trending_symbols = get_new_col_values(
                self.price_sheet, col_index = 1, 
                starting_row_index = 1,
                input_list = trending_symbols)


        new_col_index = get_new_col_index(self.price_sheet)
        append_column(self.price_sheet) 
        insert_timestamp_header(self.price_sheet, new_col_index)
    
        append_column(self.watch_sheet)
        insert_timestamp_header(self.watch_sheet, new_col_index)


        current_symbols = self.price_sheet.col_values(1)[1:]
        num_current_symbols = len(current_symbols)

        #append new symbols to end of first column
        fill_column(col_index = 1, 
                sheet = self.price_sheet,
                data = new_trending_symbols,
                start_row_index = num_current_symbols + 2) 
    
        fill_column(col_index = 1, 
                sheet = self.watch_sheet,
                data = new_trending_symbols,
                start_row_index = num_current_symbols + 2)

        time.sleep(20)
    
        tracked_symbols = self.price_sheet.col_values(1)[1:]

        base_url = 'https://stocktwits.com/symbol/'
        prices = []
        watchers = []
        for symbol in tracked_symbols:
            ticker_url = base_url + symbol
            price, watch_count = self.get_trending_symbol_info(ticker_url)
            prices.append(price)
            watchers.append(watch_count)
            time.sleep(1)
       

        fill_column(col_index = new_col_index,
                sheet = self.price_sheet,
                data = prices,
                start_row_index = 2)
        
        fill_column(col_index = new_col_index,
                sheet = self.watch_sheet, 
                data = watchers,
                start_row_index = 2)

        '''
        for index, symbol in enumerate(new_symbols):
            self.sheet.update_cell(num_current_symbols + (index+1), 1, symbol)
        
        for index, symbol in enumerate(scraped_symbols):
            if symbol in current_symbols:
                symbol_index = current_symbols.index(symbol)
                print(f'{symbol} is in the current symbols list @ position: {symbol_index + 1} ')
                self.sheet.update_cell(index+1, 2, prices[index])
            else:
                print(f'{symbol} is not in the current sumbols list')
        print(len(current_symbols))
        '''
        
if __name__ == "__main__":
    TSS = TrendingSymbolScraper()
    TSS.execute()
