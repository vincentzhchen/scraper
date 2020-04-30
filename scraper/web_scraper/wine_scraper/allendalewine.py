"""Scraper module for allendalewine.com.

"""

# STANDARD LIB
import re
import bs4
import pandas as pd
import requests

# PROJECT LIB
from scraper.util import scraper_io
from scraper.web_scraper.wine_scraper import constants as ws_const

HTML = "https://www.allendalewine.com/"

RESULTS_PER_PAGE = 100  # easier if constant


def get_html_format(session, page_name="search"):
    """Derive the html base link format from an instantiated session.

    Each session has a unique session key attached to the page.

    Args:
        session (request.session): a html request session.
        page_name (str, default: "search"): base page to query.

    Returns:
        html_format (str): returns html base link.
    """
    link = HTML + page_name
    print("Making request to {}".format(link))
    request = session.get(link)
    soup = bs4.BeautifulSoup(request.text, "lxml")
    page_links = [
        a['href'] for a in soup.find_all("a", href=True)
        if "/scan/MM" in a['href']
    ]

    if not page_links:  # do this if only one page of results
        return link

    sample_link = page_links[0]
    # each session has a unique key, retrieve this
    # eg. https://www.allendalewine.com/scan/MM=ab74b62767f10ebd8144523111d08f19:50:99:50?mv_more_ip=1&mv_nextpage=results&pf=sql&id=sbI4KBZv
    session_cache = re.findall(r"scan\/MM=\w*", sample_link)[0]
    html_format = HTML + session_cache
    return html_format


def get_html_formats(session):
    """Derive the html base link formats from an instantiated session.

    Args:
        session (request.session): a html request session.

    Returns:
        all_formats (list of str): returns html base links.
    """
    all_formats = []
    pages = [
        r"r/Cats/Red%20Wine", r"r/Cats/White%20Wine",
        r"results?countryid=&regionid=&catid=1088",
        r"results?countryid=&regionid=&catid=1060",
        r"results?countryid=&regionid=&catid=1211",
        r"results?countryid=&regionid=&catid=1438",
        r"results?countryid=&regionid=&catid=1361",
        r"results?countryid=&regionid=&catid=1369",
        r"results?countryid=&regionid=&catid=1021"
    ]
    for page in pages:
        html = get_html_format(session, page_name=page)
        if html is not None:
            all_formats.append(html)
    return all_formats


def link_generator(html_format,
                   min_item=0,
                   max_item=RESULTS_PER_PAGE,
                   items_per_page=RESULTS_PER_PAGE):
    """Create proper html link for querying.

    Add item index here if applicable.

    Args:
        html_format (str): the base html link to be modified with the
            item index.
        min_item (int, default 1): min item index.
        max_item (int, default RESULTS_PER_PAGE): max item index.
        items_per_page (int, default RESULTS_PER_PAGE): items to
            return per page.

    Returns:
        link (str): returns final html link for querying.
    """
    link = html_format
    if r"scan/MM=" in link:
        link = link + ":{}:{}:{}".format(min_item, max_item, items_per_page)
    return link


def query_one_page(session, html_link):
    """Query a single web page of a given session and html.

    Args:
        session (request.session): a html request session.
        html_link (str): link to the desired page to scrape.

    Returns:
        df (pd.DataFrame): returns a dataframe
            with ws_const.WINE_SCRAPER_OUTPUT_COLS
    """
    print("QUERYING items from {}".format(html_link))
    request = session.get(html_link)
    soup = bs4.BeautifulSoup(request.text, "lxml")
    results_list = "".join(map(str, soup.find_all(id="itemResultsList")))
    results_list = results_list.replace("\n", "")
    results_list = results_list.split("itemTitle")
    df = pd.DataFrame(results_list, columns=["RAW_DATA_STR"])
    if df.empty:
        print("NO DATA found, returning empty df.")
        return pd.DataFrame()

    df["SRC"] = HTML
    df["QUERY"] = html_link
    df["AS_OF_DATE"] = pd.to_datetime("today")

    df = get_metadata_from_query_result(df)

    df = df[ws_const.WINE_SCRAPER_OUTPUT_COLS]
    return df


def query_all_pages(session, html_format):
    """Query all item pages until no results come back.

    For a single html base format, there is an unknown number of items.
    E.g. we don't know how many red wines are in the red wine category.
    Given the base link for red wines, need to generate and query
    individual result pages.

    Args:
        session (request.session): a html request session.
        html_format (str): the base html link to be modified with the
            item index.

    Returns:
        res (pd.DataFrame): returns a dataframe of all queries.
    """
    all_dfs = []
    min_item = 0
    max_item = 100

    prev_html_link = None
    while True:
        html_link = link_generator(html_format, min_item, max_item)
        if html_link == prev_html_link:
            # breaking condition (don't query same link twice)
            break
        df = query_one_page(session, html_link)
        if not df.empty:
            all_dfs.append(df)
            min_item += RESULTS_PER_PAGE
            max_item += RESULTS_PER_PAGE
        else:
            break
        prev_html_link = html_link

    res = pd.concat(all_dfs, ignore_index=True)
    return res


def get_metadata_from_query_result(df):
    """Generate metadata from query result dataframe.

    Args:
        df (pd.DataFrame): dataframe with ["RAW_DATA_STR"]

    Returns:
        df (pd.DataFrame): returns data frame with all parsed metadata.
    """
    df = df.copy()  # do not modify input

    df["BRAND"] = df["RAW_DATA_STR"].str.findall('(?<=brand">).*?(?=<)')
    # str.findall returns a list of one element, flatten this
    df["BRAND"] = df["BRAND"].apply(lambda x: x[0].strip() if x else None)
    df = df[df["BRAND"].notnull()].copy()

    df["TITLE"] = df["RAW_DATA_STR"].str.findall('(?<=title">).*?(?=<)')
    df["TITLE"] = df["TITLE"].apply(lambda x: x[0].strip())

    df["VINTAGE"] = df["RAW_DATA_STR"].str.findall(
        r'(?<=vintageAge">)\w.*?(?=<)')
    # some items have no vintage, so can be None
    df["VINTAGE"] = df["VINTAGE"].apply(lambda x: x[0] if x else None)

    df["NAME"] = (
        df["BRAND"] + " " + df["TITLE"] + " " +
        df["VINTAGE"].fillna("")).str.strip()  # strip trailing spaces

    df["BASE_PRICE"] = df["RAW_DATA_STR"].str.findall(
        r'(?<=listprice">\$)\w.*?(?=<)')
    df["BASE_PRICE"] = df["BASE_PRICE"].apply(
        lambda x: float(x[0].replace(",", "")) if x else None)

    df["PRICE"] = df["RAW_DATA_STR"].str.findall(
        r'(?<=priceSale">\$)\w.*?(?=<)')
    df["PRICE"] = df["PRICE"].apply(lambda x: float(x[0].replace(",", ""))
                                    if x else None)
    df["PRICE"] = df["PRICE"].where(df["PRICE"].notnull(), df["BASE_PRICE"])

    df["IS_ON_SALE"] = df["BASE_PRICE"] > df["PRICE"]
    return df


def scrape_one_page(min_item=0,
                    max_item=RESULTS_PER_PAGE,
                    items_per_page=RESULTS_PER_PAGE):
    """Scrape a single page only.

    Args:
        min_item (int, default 1): min item index.
        max_item (int, default RESULTS_PER_PAGE): max item index.
        items_per_page (int, default RESULTS_PER_PAGE): items to
            return per page.

    Returns:
        df (pd.DataFrame): returns a dataframe
            with ws_const.WINE_SCRAPER_OUTPUT_COLS
    """
    session = requests.session()
    html_format = get_html_format(session)
    html_link = link_generator(html_format, min_item, max_item, items_per_page)
    df = query_one_page(session, html_link)
    return df


def scrape():
    """Scrape all pages.

    Returns:
        df (pd.DataFrame): returns a dataframe
            with ws_const.WINE_SCRAPER_OUTPUT_COLS
    """
    all_dfs = []
    session = requests.session()
    for html_format in get_html_formats(session):
        df = query_all_pages(session, html_format)
        all_dfs.append(df)
    df = pd.concat(all_dfs, ignore_index=True)
    return df


if __name__ == "__main__":
    scraper_io.to_csv(scrape(), "allendalewine_catalog")
