from dataclasses import dataclass, field
from typing import ClassVar
from enum import Enum, auto


@dataclass
class StocktwitsSymbol:
    """ """

    base_url: ClassVar[str] = "https://stocktwits.com/symbol"
    ticker: str = field(compare=False)
    watch_count: str = ""
    price: str = ""

    def __post_init__(self):
        self.preprocess_ticker()

    def preprocess_ticker(self):
        # for crypto tickers
        if "-" in self.ticker:
            self.ticker = self.ticker.replace("-", ".")

    @property
    def url(self) -> str:
        return self.base_url + f"/{self.ticker}"


class RankingCategory(Enum):
    """Stocktwits Ranking Categories"""

    TRENDING = auto()
    WATCHERS = auto()
    MOST_ACTIVE = auto()


@dataclass
class TrendingStocktwitsSymbol(StocktwitsSymbol):

    category: RankingCategory = field(default=RankingCategory.TRENDING, compare=False)
    val: str = ""
