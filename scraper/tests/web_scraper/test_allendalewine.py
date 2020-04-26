"""All unit tests for allendalewine module.

"""

from scraper.web_scraper.wine_scraper import allendalewine

def test_scrape_one_page_001():
    allendalewine.scrape_one_page()

def test_scrape_one_page_002():
    allendalewine.scrape_one_page(200, 300)

def test_scrape_one_page_003():
    allendalewine.scrape_one_page(9999, 10000)
