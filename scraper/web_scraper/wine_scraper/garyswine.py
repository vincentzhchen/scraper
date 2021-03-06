"""Scraper module for garyswine.com.

"""

# STANDARD LIB
import pandas as pd

# PROJECT LIB
from scraper.util import scraper_io
from scraper.web_scraper.wine_scraper import constants as ws_const

HTML = "https://www.garyswine.com/"
HTML_FORMAT = HTML + "wines/?page={}&l={}"  # need a page number and result size

RESULTS_PER_PAGE = 100  # easier if constant


def query_one_page(page_num):
    """Query a single web page of a page num.

    Args:
        page_num (int): page number of results to query.

    Returns:
        df (pd.DataFrame): returns a dataframe
            with ws_const.WINE_SCRAPER_OUTPUT_COLS
    """
    print("QUERYING page {}".format(page_num))
    query = HTML_FORMAT.format(page_num, RESULTS_PER_PAGE)
    result = pd.read_html(query)
    if not result[2:-2]:
        print("NO DATA found, returning empty df.")
        return pd.DataFrame()

    df = pd.concat(result[2:-2])
    df.columns = ["METADATA", "RAW_DATA_STR"]
    df = df[["RAW_DATA_STR"]].dropna()

    df["SRC"] = HTML
    df["QUERY"] = query
    df["AS_OF_DATE"] = pd.to_datetime("today")

    df = get_metadata_from_query_result(df)

    df = df[ws_const.WINE_SCRAPER_OUTPUT_COLS]
    return df


def query_all_pages():
    """Query all item pages until no results come back.

    Returns:
        res (pd.DataFrame): returns a dataframe of all queries.
    """
    all_dfs = []
    page_num = 1
    while True:
        df = query_one_page(page_num)
        if not df.empty:
            all_dfs.append(df)
            page_num += 1
        else:
            break

    return pd.concat(all_dfs, ignore_index=True)


def get_metadata_from_query_result(df):
    """Generate metadata from query result dataframe.

    Args:
        df (pd.DataFrame): dataframe with ["RAW_DATA_STR"]

    Returns:
        df (pd.DataFrame): returns data frame with all parsed metadata.
    """
    df["NAME"] = df["RAW_DATA_STR"].str.findall("content_name.*?,").apply(
        lambda x: x[0].split(":")[1][:-1].strip() if x else None)

    df = df[df["NAME"].notnull()].copy()

    # this should return a list of one price [reg. price] if no sale and
    # two prices [sale price, reg. price] if sale
    regex = r"\$\d{1,3}(?:[,]\d{3})*(?:[.]\d{2})"
    #       |--|------|------------|-----------|
    #       |$ | 1-3  | 3 digits   | 2 digits  |
    #       |  |digits| repeated   |  (cents)  |
    #       |  |      |            |           |
    df["PRICES"] = df["RAW_DATA_STR"].str.findall(regex)
    df["PRICE"] = df["PRICES"].apply(lambda x: x[0][1:].replace(",", ""))
    df["BASE_PRICE"] = df["PRICES"].apply(
        # if one price, then take the single listed price
        lambda x: x[1][1:].replace(",", "")
        if (x[1:2]) else x[0][1:].replace(",", ""))

    df["IS_ON_SALE"] = df["BASE_PRICE"] > df["PRICE"]

    return df


def scrape_one_page(page_num):
    """Scrape a single page only.

    Args:
        page_num (int): page number of results to query.

    Returns:
        df (pd.DataFrame): returns a dataframe
            with ws_const.WINE_SCRAPER_OUTPUT_COLS
    """
    df = query_one_page(page_num)
    return df


def scrape():
    """Scrape all pages.

    Returns:
        df (pd.DataFrame): returns a dataframe
            with ws_const.WINE_SCRAPER_OUTPUT_COLS
    """
    df = query_all_pages()
    return df


if __name__ == "__main__":
    scraper_io.to_csv(scrape(), "garyswine_catalog")
