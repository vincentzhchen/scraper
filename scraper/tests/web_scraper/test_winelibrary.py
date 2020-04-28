"""All unit tests for winelibrary module.

"""

# PROJECT LIB
from scraper.web_scraper.wine_scraper import winelibrary

def test_scrape_one_page_001():
    assert not winelibrary.scrape_one_page(1).empty

def test_scrape_one_page_002():
    assert not winelibrary.scrape_one_page(2).empty

def test_scrape_one_page_003():
    assert winelibrary.scrape_one_page(999).empty
