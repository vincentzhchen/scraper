"""All unit tests for garyswine module.

"""

# PROJECT LIB
from scraper.web_scraper.wine_scraper import garyswine

def test_scrape_one_page_001():
    garyswine.scrape_one_page(1)

def test_scrape_one_page_002():
    garyswine.scrape_one_page(9)

def test_scrape_one_page_003():
    garyswine.scrape_one_page(999)
