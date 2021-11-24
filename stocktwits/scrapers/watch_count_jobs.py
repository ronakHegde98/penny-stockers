from crawlers import WatchSymbolCrawler

if __name__ == "__main__":
    wcs = WatchSymbolCrawler(
        user_client="rob", spreadsheet="Penny Stalkers", sheet="Stocktwits"
    )
    wcs.execute()
