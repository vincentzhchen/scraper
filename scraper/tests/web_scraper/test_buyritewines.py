"""All unit tests for buyritewines module.

"""

from scraper.web_scraper.wine_scraper import buyritewines

def test_scrape_one_page_001():
    buyritewines.scrape_one_page(1)

def test_scrape_one_page_002():
    buyritewines.scrape_one_page(2)

def test_scrape_one_page_003():
    buyritewines.scrape_one_page(999)
