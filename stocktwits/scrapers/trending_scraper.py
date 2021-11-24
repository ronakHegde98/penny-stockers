"""
"""
from models import RankingCategory, TrendingStocktwitsSymbol
from symbol_scraper import StocktwitsSymbolScraper
import requests
from typing import Dict, Any, List


class RankingScraper:
    BASE_URL: str = "https://api.stocktwits.com/api/2/charts/"

    endpoint_mapping = {
        RankingCategory.TRENDING: "ts",
        RankingCategory.MOST_ACTIVE: "m_day",
        RankingCategory.WATCHERS: "wl_ct_day",
    }

    def __init__(self, category: RankingCategory):
        self.category = category

    @property
    def endpoint(self):
        return self.endpoint_mapping[self.category]

    @property
    def url(self):
        return self.BASE_URL + self.endpoint

    def filter_data(self, data_dict: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """ """
        # TODO: refactor => take args as params
        data = data_dict.get("stocks")

        stock_table_values = data_dict.get("table").get(self.endpoint)
        for entry in stock_table_values:
            id, val = entry.values()
            data[str(id)]["val"] = str(val)

        return data

    def grab_data(self) -> Dict[str, Any]:
        """ """
        # TODO: add error handling
        res = requests.get(self.url)
        return res.json()

    def scrape(self) -> List[TrendingStocktwitsSymbol]:
        data = self.grab_data()
        filtered_data = self.filter_data(data)

        symbols = []
        for data in filtered_data.values():
            symbol = TrendingStocktwitsSymbol(
                ticker=data.get("symbol"), category=self.category, val=data.get("val")
            )
            symbols.append(symbol)
            print(symbol)

        # symbol_scraper = StocktwitsSymbolScraper()
        # symbol_scraper.scrape_symbols_data(symbols=symbols)
        return symbols


# import time

# trending_scraper = RankingScraper(category=RankingCategory.TRENDING)
# print("Scraping trending.....")
# trending_scraper.scrape()

# trending_scraper = RankingScraper(category=RankingCategory.MOST_ACTIVE)
# print("\nScraping most active.....")
# trending_scraper.scrape()

# trending_scraper = RankingScraper(category=RankingCategory.WATCHERS)
# print("\nScraping watchers......")
# trending_scraper.scrape()
