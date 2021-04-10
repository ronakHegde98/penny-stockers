from scraper import TrendingSymbolScraper
import time

if __name__ == "__main__":
    # THREE SCRAPERS
    
    spreadsheet = 'Penny Stalkers'
    
    time.sleep(30)
    #watchers
    tss = TrendingSymbolScraper(
            spreadsheet = spreadsheet,
            scraping_category = 'watchers',
            price_sheet = 'Watchers_Price',
            watch_sheet = 'Watchers_WatchCount')
    tss.execute()   
    time.sleep(10)
    
    # trending
    tss = TrendingSymbolScraper(
            spreadsheet = spreadsheet,
            scraping_category = 'trending',
            price_sheet = 'Trending_Price',
            watch_sheet = 'Trending_WatchCount')
    tss.execute()
    time.sleep(10)
    
    # most-active 
    tss = TrendingSymbolScraper(
            spreadsheet = spreadsheet,
            scraping_category = 'most-active',
            price_sheet = 'MostActive_Price',
            watch_sheet = 'MostActive_WatchCount')
    tss.execute()
