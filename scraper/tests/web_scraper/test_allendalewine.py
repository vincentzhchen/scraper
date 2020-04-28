"""All unit tests for allendalewine module.

"""

# PROJECT LIB
from scraper.web_scraper.wine_scraper import allendalewine

def test_scrape_one_page_001():
    assert not allendalewine.scrape_one_page().empty

def test_scrape_one_page_002():
    assert not allendalewine.scrape_one_page(200, 300).empty

def test_scrape_one_page_003():
    assert allendalewine.scrape_one_page(9999, 10000).empty
