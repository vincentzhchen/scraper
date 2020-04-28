"""All unit tests for garyswine module.

"""

# PROJECT LIB
from scraper.web_scraper.wine_scraper import garyswine

def test_scrape_one_page_001():
    assert not garyswine.scrape_one_page(1).empty

def test_scrape_one_page_002():
    assert not garyswine.scrape_one_page(9).empty

def test_scrape_one_page_003():
    assert garyswine.scrape_one_page(999).empty
