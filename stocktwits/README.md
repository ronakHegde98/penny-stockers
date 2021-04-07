Stocktwits Scraper

> Track prices and watch counts for tracked and trending stocks! Keep track of price changes 📈

## Description

#### Sources
 1. [Stocktwits](https://stocktwits.com/)

#### Technologies
 - Language: Python 3.8.5
 - Web Framework: Flask
 - Google Sheets API ([GSpread - Python API Client](https://github.com/burnash/gspread))
 - Scraping: BeautifulSoup and Selenium 

# Getting Started

1. Clone this repo
```
git clone https://github.com/ronakHegde98/penny-stockers.git
```
2. Create a virtual environment
```
cd stocktwits; python3 -m venv venv
```
3. Install Project Dependencies
```
pip install -r requirements.txt
```
4. (If you are tracking on Google Sheets):  Place google_creds.json in `config/`
5. To run WatchCountScraper

    ```python
    from scraper import WatchCountScraper
    
    wcs = WatchCountScraper(sheet = your_sheet)
    wcs.execute()
    ```

6. To run the TrendingSymbolScraper 

    ```python
    from scraper import TrendingSymbolScraper
    
    price_gsheet = 'Watchers_Price'
    watch_count_gsheet = 'Watchers_WatchCount'
    tss = TrendingSymbolScraper(symbol_category = 'watchers',
                                   price_sheet = price_gsheet,
                                   watch_sheet = watch_count_gsheet)
    tss.execute()
    ```


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.


<!-- CONTACT -->
## Contact

Ronak Hegde - [Linkedin](https://www.linkedin.com/in/ronakhegde)


* [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)

