"""Scraper module for allendalewine.com.

"""

# STANDARD LIB
import os
import re
import bs4
import pandas as pd
import requests

# PROJECT LIB
from scraper.settings import settings
from scraper.web_scraper.wine_scraper import constants as ws_const

HTML = "https://www.allendalewine.com/"

RESULTS_PER_PAGE = 100  # easier if constant


def get_html_format(session):
    """Derive the html base link from an instantiated session.

    Args:
        session (request.session): a html request session.

    Returns:
        html_format (str): returns html base link.
    """
    request = session.get(HTML + "search")
    soup = bs4.BeautifulSoup(request.text)
    page_links = [
        a['href'] for a in soup.find_all("a", href=True)
        if "/scan/MM" in a['href']
    ]
    sample_link = page_links[0]
    # each session has a unique key, retrieve this
    # eg. https://www.allendalewine.com/scan/MM=ab74b62767f10ebd8144523111d08f19:50:99:50?mv_more_ip=1&mv_nextpage=results&pf=sql&id=sbI4KBZv
    session_cache = re.findall(r"scan\/MM=\w*", sample_link)[0]
    html_format = HTML + session_cache
    return html_format


def query_one_page(session,
                   html_format,
                   min_item=0,
                   max_item=100,
                   items_per_page=100):
    """Query a single web page of a given session and html.

    Args:
        session (request.session): a html request session.
        html_format (str): the base html link to be modified with the
            item index.
        min_item (int, default 1): min item index.
        max_item (int, default 100): max item index.
        items_per_page (int, default 100): items to return per page.

    Returns:
        df (pd.DataFrame): returns a dataframe
            with ws_const.WINE_SCRAPER_OUTPUT_COLS
    """
    print("QUERYING items {} to {}".format(min_item, max_item))
    query = html_format + ":{}:{}:{}".format(min_item, max_item,
                                             items_per_page)
    request = session.get(query)
    soup = bs4.BeautifulSoup(request.text)
    results_list = "".join(map(str, soup.find_all(id="itemResultsList")))
    results_list = results_list.replace("\n", "")
    results_list = results_list.split("itemTitle")
    df = pd.DataFrame(results_list, columns=["RAW_DATA_STR"])
    if df.empty:
        print("NO DATA found, returning empty df.")
        return pd.DataFrame()

    df["SRC"] = HTML
    df["QUERY"] = query
    df["AS_OF_DATE"] = pd.to_datetime("today")

    df = get_metadata_from_query_result(df)

    df = df[ws_const.WINE_SCRAPER_OUTPUT_COLS]
    return df


def query_all_pages(session, html_format):
    """Query all item pages until no results come back.

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
    while True:
        df = query_one_page(session, html_format, min_item, max_item,
                            RESULTS_PER_PAGE)
        if not df.empty:
            all_dfs.append(df)
            min_item += RESULTS_PER_PAGE
            max_item += RESULTS_PER_PAGE
        else:
            break

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


def scrape():
    """Main scrape method.

    """
    session = requests.session()
    html_format = get_html_format(session)
    df = query_all_pages(session, html_format)
    now = pd.to_datetime("today").strftime("%Y%m%d_%H%M%S%f")
    out_file = "allendalewine_catalog_{}.csv".format(now)
    df.to_csv(os.path.join(settings.DATA_DIRECTORY, out_file), index=False)


if __name__ == "__main__":
    scrape()
