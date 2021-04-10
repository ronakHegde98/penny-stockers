from util import get_current_datetime, is_int
from scraper_util import get_web_driver, get_page_source, kill_chrome, get_soup_object
from sheets_util import *

from bs4 import BeautifulSoup
from pathlib import Path
from typing import Tuple, List, Dict
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

    def __init__(self, spreadsheet: str):
        gsheets_client = get_gsheets_client()
        self.spreadsheet = gsheets_client.open(spreadsheet)
    
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
    
    def __init__(self, spreadsheet: str, sheet: str):
        super().__init__(spreadsheet)
        self.sheet = get_sheet(spreadsheet = self.spreadsheet, sheet_name = sheet)

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

    ranking_categories = ['trending', 'most-active', 'watchers']
    
    def __init__(self, spreadsheet: str, scraping_category: str, price_sheet: str, watch_sheet: str) -> None:
        super().__init__(spreadsheet)
        
        self.validate_scraping_category(scraping_category)
        self.TRENDING_URL = self.BASE_URL + f'/rankings/{scraping_category}'
         
        self.price_sheet = get_sheet(self.spreadsheet, price_sheet)
        self.watch_sheet = get_sheet(self.spreadsheet, watch_sheet)
        self.sheets = [self.price_sheet, self.watch_sheet]

    def validate_scraping_category(self, category: str) -> None:
        if(not category.lower() in self.ranking_categories):
            supported_categories_str = ', '.join(self.ranking_categories)
            raise ValueError(f"'{category}' is not a valid category. Supported categories: {supported_categories_str}")      

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

    def get_symbols_data(self, symbols: List[str]) -> Tuple[Dict[str,str], Dict[str,str]]:
        prices = {}
        watch_counts = {}

        for symbol in symbols:
            ticker_url = self.SYMBOL_BASE_URL + symbol
            price, watch_count = self.scrape_symbol_data(ticker_url)
            prices[symbol] = price
            watch_counts[symbol] = watch_count
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
        
        # avoid update/delete errors
        price_sheet_symbols = get_column_values(sheet = self.price_sheet, col_index = 1)
        watch_sheet_symbols = get_column_values(sheet = self.watch_sheet, col_index = 1)
        
        trending_symbols = self.get_trending_symbols()
        
        new_price_sheet_symbols = set(trending_symbols) - set(price_sheet_symbols)
        new_watch_sheet_symbols = set(trending_symbols) - set(watch_sheet_symbols)

        # both sheets should be on same column
        new_col_index = get_new_col_index(self.price_sheet)
        
        new_symbols_list = [new_price_sheet_symbols, new_watch_sheet_symbols]
        num_current_symbols = [len(price_sheet_symbols), len(watch_sheet_symbols)]

        for sheet, new_symbols, num_current_symbols in zip(self.sheets,
                                                           new_symbols_list,
                                                           num_current_symbols):
            setup_column(
                    sheet = sheet,
                    append_new_column = True,
                    new_col_index = new_col_index)
            
            if(new_symbols):
                fill_column(
                    col_index = 1,
                    sheet = sheet,
                    data = new_symbols,
                    start_row_index = num_current_symbols + 2)
                
                #bump this number up
                time.sleep(10)
            
        tracked_price_symbols = price_sheet_symbols + list(new_price_sheet_symbols)
        tracked_watch_symbols = watch_sheet_symbols + list(new_watch_sheet_symbols)
        tracked_symbols = list(set(tracked_price_symbols + tracked_watch_symbols))
        
        prices, watch_counts = self.get_symbols_data(symbols = tracked_symbols)

        tracked_prices = [prices[symbol] for symbol in tracked_price_symbols]
        tracked_watch_counts =  [watch_counts[symbol] for symbol in tracked_watch_symbols]
        
        for sheet, data in zip(self.sheets, [tracked_prices, tracked_watch_counts]):
            time.sleep(20)
            fill_column(col_index = new_col_index,
                    sheet = sheet,
                    data = data,
                    start_row_index = 2) 
