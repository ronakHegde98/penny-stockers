from crawlers import RankingCrawler
from models import RankingCategory
import time

spreadsheet = "Penny Stalkers"
crawler = RankingCrawler(
    user_client="tommy", spreadsheet=spreadsheet, category=RankingCategory.MOST_ACTIVE
)
crawler.scrape_trending_value(sheet="MostActive_MessageCount")
crawler.scrape_price_and_follower_count(
    price_sheet="MostActive_Price", watch_sheet="MostActive_WatchCount"
)

time.sleep(10)
crawler = RankingCrawler(
    user_client="tommy", spreadsheet=spreadsheet, category=RankingCategory.WATCHERS
)
crawler.scrape_trending_value(sheet="Watchers_NewCount")
crawler.scrape_price_and_follower_count(
    price_sheet="Watchers_Price", watch_sheet="Watchers_WatchCount"
)
