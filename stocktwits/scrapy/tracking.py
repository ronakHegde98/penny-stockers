from scraper import WatchCountScraper

if __name__ == "__main__":
    wcs = WatchCountScraper(spreadsheet = 'Penny Stalkers', sheet = 'Stocktwits')
    wcs.execute()

