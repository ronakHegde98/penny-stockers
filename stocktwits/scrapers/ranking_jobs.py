from crawlers import RankingCrawler

spreadsheet = "Penny Stalkers"
crawler = RankingCrawler(
    user_client="ronak", spreadsheet=spreadsheet, category=RankingCategory.TRENDING
)
crawler.scrape_trending_value(sheet="Trending_Score")
crawler.scrape_price_and_follower_count(price_sheet="Trending_Price", watch_sheet="")
