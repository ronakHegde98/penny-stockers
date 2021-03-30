import sys
sys.path.insert(0, '/home/ubuntu/penny-stockers/')

from stocktwits.config.creds import get_gsheets_client
from util import get_current_datetime, is_int
from bs4 import BeautifulSoup
from pathlib import Path
from pprint import pprint
import requests
import random
import time
import gspread
import logging
import os


daily_followers_log_file_name = 'daily_stocktwits_scraper.log'
daily_followers_log_file_path = os.path.join(Path(os.getcwd()).parent,'logs',daily_followers_log_file_name)

logging.basicConfig(
    level=logging.ERROR,
    format="{asctime} {levelname: <8} {message}",
    style="{",
    filename = daily_followers_log_file_path,
    filemode='a'
)


class StockTwitsScraper:
    def __init__(self):
        self.STOCKTWITS_BASE_URL = 'https://www.stocktwits.com/symbol/'
        self.spreadsheet_name = "Penny Stalkers"
        self.sheet_name = "Stocktwits"

    def get_follower_count(self, ticker_url: str) -> int:

        r = requests.get(ticker_url)
        soup = BeautifulSoup(r.content, 'lxml')
        
        try:
            follower_count = soup.find('strong').text
            if(not is_int(follower_count)):

                #try once more
                count = self.get_follower_count(ticker_url)
                if(not is_int(count)):
                    symbol = ticker_url.split('/')[-1]
                    logger.error(f"follower count of {symbol} was non-int: {follower_count}")
                    return None
        except AttributeError as e:
            logging.info(f"Not able to scrape: {ticker_url}")
            return None
        except Exception as e:
            logging.error(
                f"There was an error with scraping followers:", exc_info=True)

        return follower_count

    def scrape_followers(self, tickers: list) -> list:

        follower_counts = []

        for ticker in tickers:
            if(ticker):
                ticker_url = self.STOCKTWITS_BASE_URL + ticker
                follower_count = self.get_follower_count(ticker_url)

                # in case stocktwits has an issue
                if(follower_count):
                    follower_counts.append(follower_count)
                    print(ticker, follower_count)
                else:
                    follower_counts.append('')
            else:
                follower_counts.append('')

            time.sleep(random.randint(0, 2))

        return follower_counts

    def insert_col(self, follower_counts: list, sheet, col_index) -> None:
        time.sleep(50)

        for index, follow_count in enumerate(follower_counts):
            if(index % 50 == 0):
                time.sleep(10)
            try:
                sheet.update_cell(index + 2, col_index, follow_count)
                print(index)
                time.sleep(1)
            except APIError as e:
                logging.critical(
                    "There was an error with Google API requests", exc_info)

    def execute(self):
        client = get_gsheets_client()
        spreadsheet = client.open(self.spreadsheet_name)
        sheet = spreadsheet.worksheet(self.sheet_name)

        # tickers are the left most values and non
        tickers = sheet.col_values(1)[1:]

        follower_counts = []

        start_time = time.time()
        follower_counts = self.scrape_followers(tickers)
        logging.info("--- %s seconds to scrape symbols ---" % (time.time() - start_time))


        # insert new column and add column header
        new_col_index = len(sheet.row_values(1)) + 1
        sheet.add_cols(1)
        sheet.update_cell(1, new_col_index, get_current_datetime())

        self.insert_col(follower_counts, sheet, new_col_index)

if __name__ == "__main__":
    scraper = StockTwitsScraper()
    scraper.execute()
