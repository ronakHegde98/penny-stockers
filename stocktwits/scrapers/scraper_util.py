from selenium.common.exceptions import WebDriverException  # type: ignore
from selenium import webdriver  # type: ignore
import pandas as pd  # type: ignore
import os
from bs4 import BeautifulSoup
from typing import List, Union

import httpx
import asyncio

CHROME_DRIVER_PATH = "/usr/bin/chromedriver"


class WebsiteNotReachableException(Exception):
    """whenever we cannot reach a given url"""

    def __init__(self, msg: str):
        super().__init__(msg)


def get_chrome_options() -> webdriver.ChromeOptions:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-usage")
    return options


def get_web_driver():
    if os.path.exists(CHROME_DRIVER_PATH):
        options = get_chrome_options()
        return webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=options)
    else:
        return None


def get_page_source(wd: webdriver, url: str) -> str:
    page_source = None
    try:
        wd.get(url)
        page_source = wd.page_source
    except WebDriverException as e:
        raise WebsiteNotReachableException(f"{url}")
    return page_source


def kill_chrome() -> None:
    os.system("pkill -9 -f chrome")


async def batch_async_http_requests(urls: List[str]) -> List[str]:
    """ """
    async with httpx.AsyncClient() as client:
        tasks = (client.get(url) for url in urls)
        reqs = await asyncio.gather(*tasks)

    return [req.text for req in reqs]


""" BEAUTIFULSOUP UTIL FUNCTIONS """


def get_soup_object(response_content: str) -> BeautifulSoup:
    """
    Note: possible to get page even if content is not desired
    """
    # TODO: error handling here if empty string
    return BeautifulSoup(response_content, "lxml")
