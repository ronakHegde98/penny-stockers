from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bs4 import BeautifulSoup
    from models import StocktwitsSymbol

import asyncio
from typing import List
from scraper_util import batch_async_http_requests, get_soup_object


class StocktwitsSymbolScraper:
    """scrape symbol"""

    @staticmethod
    def scrape_price(soup: BeautifulSoup) -> str:
        price_class = "st_3zYaKAL"
        price_tag = soup.find("span", attrs={"class": price_class})
        if not price_tag:
            return ""
        return price_tag.text

    @staticmethod
    def scrape_watch_count(soup: BeautifulSoup) -> str:
        watch_count_tag = soup.find("strong")
        if not watch_count_tag:
            return ""
        return watch_count_tag.text

    @staticmethod
    def scrape_pages(symbols: List[StocktwitsSymbol]) -> List[str]:
        symbol_urls = [symbol.url for symbol in symbols]
        reqs = asyncio.run(batch_async_http_requests(urls=symbol_urls))
        return reqs

    @classmethod
    def scrape_symbols_data(cls, symbols: List[StocktwitsSymbol]) -> None:
        """scrape all supported data related to individual stocktwits symbols"""

        reqs = cls.scrape_pages(symbols)
        soups = [get_soup_object(req) for req in reqs]

        for symbol, symbol_soup in zip(symbols, soups):
            symbol.price = cls.scrape_price(symbol_soup)
            symbol.watch_count = cls.scrape_watch_count(symbol_soup)
            print(symbol)  # TODO: add logging
