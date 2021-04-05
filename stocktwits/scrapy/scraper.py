from util import get_current_datetime, is_int
from scraper_util import get_web_driver, get_page_source, kill_chrome, get_soup_object
from sheets_util import *

from bs4 import BeautifulSoup
from pathlib import Path
from typing import Tuple, List
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

# exception handling
from selenium.common.exceptions import WebDriverException

class StockTwitsScraper:  

    BASE_URL = 'https://stocktwits.com'
    SYMBOL_BASE_URL = BASE_URL + '/symbol/'
    spreadsheet_name = 'Penny Stalkers'

    def __init__(self):
        gsheets_client = get_gsheets_client()
        self.spreadsheet = gsheets_client.open(self.spreadsheet_name)
    
    def get_symbol_price(self, soup: BeautifulSoup) -> str:
        price_class = 'st_3zYaKAL'
        price_tag = soup.find('span', attrs = {'class': price_class})
        if(price_tag):
            return price_tag.text
        else:
            return '' 
   
    def get_symbol_watch_count(self, soup: BeautifulSoup) -> str:
        watch_count_tag = soup.find('strong')
        if(watch_count_tag):
            return watch_count_tag.text
        else:
            return ''

class WatchCountScraper(StockTwitsScraper):
    
    GSHEET = 'Stocktwits'

    def __init__(self):
        super().__init__()
        self.sheet = get_sheet(spreadsheet = self.spreadsheet, sheet_name = self.GSHEET)

    def get_watch_counts(self, symbols: List[str]) -> List[str]:
        watch_counts = []

        for symbol in symbols:
            if(symbol):
                symbol_url = self.SYMBOL_BASE_URL + symbol
                soup = get_soup_object(url = symbol_url)
                if(soup):
                    watch_count = self.get_symbol_watch_count(soup)
                    watch_counts.append(watch_count)
                else:
                    watch_counts.append('')
            else:
                watch_counts.append('')

            time.sleep(random.randint(0,1))

        return watch_counts
    
    def execute(self):
        symbols = get_column_values(
                sheet = self.sheet,
                col_index = 1)
        
        watch_counts = self.get_watch_counts(symbols)
        new_col_index = get_new_col_index(self.sheet)
        
        setup_column(
                sheet = self.sheet,
                append_new_column = True,
                new_col_index = new_col_index)

        fill_column(
                col_index = new_col_index,
                sheet = self.sheet,
                data = watch_counts,
                start_row_index = 2)
                

class TrendingSymbolScraper(StockTwitsScraper):
    """ scraping the top trending symbols from a given stocktwits category in the last 24 hours"""

    PRICE_GSHEET = 'TrendingPrices'
    WATCH_COUNT_GSHEET = 'TrendingWatchCount'
    ranking_categories = ['trending', 'most-active', 'watchers']
    
    def __init__(self, scraping_category: str):
        super().__init__()

        if(self.is_valid_scraping_category(scraping_category)):
            self.TRENDING_URL = self.BASE_URL + f'/rankings/{scraping_category}'
        
        self.price_sheet = get_sheet(self.spreadsheet, self.PRICE_GSHEET)
        self.watch_sheet = get_sheet(self.spreadsheet, self.WATCH_COUNT_GSHEET)
        self.sheets = [self.price_sheet, self.watch_sheet]

    def is_valid_scraping_category(self, category: str) -> bool:
        if(category.lower() in self.ranking_categories
                and isinstance(category, str)):
            return True

    def scrape_trending_symbols(self) -> List[str]:
        wd = get_web_driver()
        trending_symbols = []

        try:
            page_html = get_page_source(wd, url = self.TRENDING_URL)
            dataframes = pd.read_html(page_html)    
            trending_df = dataframes[0]
            trending_symbols = list(trending_df['Symbol'])
        except WebDriverException:
            #TODO: logging
            pass
        except ValueError:
            #TODO: logging
            pass
        except KeyError:
            #TODO: logging
            pass
        finally:
            wd.quit() 

        return trending_symbols
    
    def get_trending_symbols(self) -> List[str]:
        kill_chrome()
        trending_symbols_raw = self.scrape_trending_symbols()
        trending_symbols = [symbol.replace('-', '.') for symbol in trending_symbols_raw]
        return trending_symbols

    def get_symbols_data(self, symbols: List[str]) -> Tuple[List[str], List[str]]:
        prices = []
        watch_counts = []

        for symbol in symbols:
            ticker_url = self.SYMBOL_BASE_URL + symbol
            price, watch_count = self.scrape_symbol_data(ticker_url)
            prices.append(price)
            watch_counts.append(watch_count)
            time.sleep(1)

        return prices, watch_counts

    def scrape_symbol_data(self, ticker_url: str) -> Tuple[str, str]:
        """ return prices and counts of trending symbols """
        price, watch_count = '', ''

        soup = get_soup_object(ticker_url)
        if(soup):
            price = self.get_symbol_price(soup)
            watch_count = self.get_symbol_watch_count(soup)
        else:
            #TODO: log an error message if the page was not reachable
            pass

        return price, watch_count

    def execute(self):
        
        current_symbols = get_column_values(
                sheet = self.price_sheet,
                col_index = 1)
        num_current_symbols = len(current_symbols)
        
        trending_symbols = self.get_trending_symbols()
        new_trending_symbols = set(trending_symbols) - set(current_symbols)
        
        if(new_trending_symbols):
            new_col_index = get_new_col_index(self.price_sheet) 
        
            for sheet in self.sheets:
                setup_column(
                        sheet = sheet,
                        append_new_column = True,
                        new_col_index = new_col_index)
                fill_column(
                        col_index = 1,
                        sheet = sheet, 
                        data = new_trending_symbols,
                        start_row_index = num_current_symbols + 2)
    
                #bump this number up
                time.sleep(10)    
        
            tracked_symbols = get_column_values(self.price_sheet, 
                    col_index = 1)
        
            prices, watch_counts = self.get_symbols_data(symbols = tracked_symbols)
        
            for sheet, data in zip(self.sheets, [prices, watch_counts]):
                time.sleep(20)
                fill_column(col_index = new_col_index,
                        sheet = sheet,
                        data = data,
                        start_row_index = 2)
        
if __name__ == "__main__":
    TSS = TrendingSymbolScraper(scraping_category = 'watchers')
    TSS.execute()

    #WCS = WatchCountScraper()
    #WCS.execute()
