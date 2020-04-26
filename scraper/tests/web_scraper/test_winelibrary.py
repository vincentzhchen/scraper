"""All unit tests for winelibrary module.

"""

# PROJECT LIB
from scraper.web_scraper.wine_scraper import winelibrary

def test_scrape_one_page_001():
    winelibrary.scrape_one_page(1)

def test_scrape_one_page_002():
    winelibrary.scrape_one_page(2)

def test_scrape_one_page_003():
    winelibrary.scrape_one_page(999)
