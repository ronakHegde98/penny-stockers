from crawlers import RankingCrawler
from models import RankingCategory

spreadsheet = "Penny Stalkers"
crawler = RankingCrawler(
    user_client="ronak", spreadsheet=spreadsheet, category=RankingCategory.TRENDING
)
print("starting trending score....")
crawler.scrape_trending_value(sheet="Trending_Score")
print("\nstarting trending price scrape")
crawler.scrape_price_and_follower_count(price_sheet="Trending_Price", watch_sheet="")
