from models import RankingCategory, StocktwitsSymbol
from symbol_scraper import StocktwitsSymbolScraper
from trending_scraper import RankingScraper

# from trending_scraper import RankingCategory, StocktwitsRankingsScraper
from sheets_util import *

from pathlib import Path
import sys
import os

# adding stocktwits module to system path
stocktwits_path = str(Path(os.getcwd()).parent) + "/"
sys.path.append(stocktwits_path)
from config.creds import get_gsheets_client


class Base:
    def __init__(self, user_client: str, spreadsheet: str):
        gsheets_client = get_gsheets_client(user_client)
        self.spreadsheet = gsheets_client.open(spreadsheet)

    def setup_and_fill_column(self, sheet, data):
        new_col_index = get_new_col_index(sheet)
        setup_column(sheet=sheet, append_new_column=True, new_col_index=new_col_index)
        fill_column(col_index=new_col_index, sheet=sheet, data=data, start_row_index=2)


class WatchSymbolCrawler(Base):
    """Scrape watch counts of stocks we are tracking"""

    def __init__(self, user_client: str, spreadsheet: str, sheet: str):
        super().__init__(user_client, spreadsheet)
        self.sheet = get_sheet(spreadsheet=self.spreadsheet, sheet_name=sheet)

    def get_watch_counts(self, tickers):
        symbols = [StocktwitsSymbol(ticker) for ticker in tickers]
        scraper = StocktwitsSymbolScraper()
        scraper.scrape_symbols_data(symbols=symbols)
        return [symbol.watch_count for symbol in symbols]

    def execute(self):
        """ """
        tickers = get_column_values(sheet=self.sheet, col_index=1)
        watch_counts = self.get_watch_counts(tickers)

        self.setup_and_fill_column(self.sheet, data=watch_counts)


class RankingCrawler(Base):
    def __init__(self, user_client: str, spreadsheet: str, category: RankingCategory):
        super().__init__(user_client, spreadsheet)
        self.trending_scraper = RankingScraper(category=category)
        self.symbol_scraper = StocktwitsSymbolScraper()

    def scrape_trending_value(self, sheet):
        sheet = get_sheet(spreadsheet=self.spreadsheet, sheet_name=sheet)
        current_symbols = get_column_values(sheet=sheet, col_index=1)
        num_current_symbols = len(current_symbols)
        trending_symbols = self.trending_scraper.scrape()
        trending_symbols_names = [sym.ticker for sym in trending_symbols]

        new_symbols = list(set(trending_symbols_names) - set(current_symbols))
        new_symbols.sort()

        if new_symbols:
            fill_column(
                col_index=1,
                sheet=sheet,
                data=new_symbols,
                start_row_index=num_current_symbols + 2,
            )

        new_col_index = get_new_col_index(sheet=sheet)
        setup_column(
            sheet=sheet,
            append_new_column=True,
            new_col_index=new_col_index,
        )

        current_symbols = get_column_values(sheet=sheet, col_index=1)
        for symbol in trending_symbols:
            symbol_index = current_symbols.index(symbol.ticker) + 2
            sheet.update_cell(symbol_index, new_col_index, symbol.val)
            time.sleep(1)

    def scrape_price_and_follower_count(
        self, price_sheet: str, watch_sheet: str
    ) -> None:

        if price_sheet:
            price_sheet = get_sheet(
                spreadsheet=self.spreadsheet, sheet_name=price_sheet
            )

        if watch_sheet:
            watch_sheet = get_sheet(
                spreadsheet=self.spreadsheet, sheet_name=watch_sheet
            )

        current_symbols = get_column_values(sheet=price_sheet, col_index=1)
        num_current_symbols = len(current_symbols)
        trending_symbols = self.trending_scraper.scrape()
        trending_symbols_names = [sym.ticker for sym in trending_symbols]

        new_symbols = list(set(trending_symbols_names) - set(current_symbols))
        new_symbols.sort()

        if new_symbols:
            fill_column(
                col_index=1,
                sheet=price_sheet,
                data=new_symbols,
                start_row_index=num_current_symbols + 2,
            )

        current_symbols = get_column_values(sheet=price_sheet, col_index=1)

        # price and watch count list
        symbols = [StocktwitsSymbol(ticker) for ticker in current_symbols]
        self.symbol_scraper.scrape_symbols_data(symbols)

        prices = [symbol.price for symbol in symbols]
        self.setup_and_fill_column(price_sheet, prices)

        if watch_sheet:
            fill_column(
                col_index=1,
                sheet=watch_sheet,
                data=new_symbols,
                start_row_index=num_current_symbols + 2,
            )

            watch_counts = [symbol.watch_count for symbol in symbols]
            self.setup_and_fill_column(watch_sheet, watch_counts)
