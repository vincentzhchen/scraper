"""All unit tests for winelibrary module.

"""

from scraper.web_scraper.wine_scraper import winelibrary

def test_scrape_one_page_001():
    winelibrary.scrape_one_page(1)

def test_scrape_one_page_002():
    winelibrary.scrape_one_page(2)
