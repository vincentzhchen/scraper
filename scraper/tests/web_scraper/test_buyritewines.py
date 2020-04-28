"""All unit tests for buyritewines module.

"""

# PROJECT LIB
from scraper.web_scraper.wine_scraper import buyritewines

def test_scrape_one_page_001():
    assert not buyritewines.scrape_one_page(1).empty

def test_scrape_one_page_002():
    assert not buyritewines.scrape_one_page(2).empty

def test_scrape_one_page_003():
    assert buyritewines.scrape_one_page(999).empty
