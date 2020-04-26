"""Scraper module for winelibrary.com.

"""

# STANDARD LIB
import os
import pandas as pd
import requests

# PROJECT LIB
from scraper.settings import settings
from scraper.web_scraper.wine_scraper import constants as ws_const

HTML = "https://winelibrary.com/"
HTML_FORMAT = HTML + "search?page={}"  # need a page number


def query_one_page(page_num):
    """Query a single web page of a page num.

    Args:
        page_num (int): page number of results to query.

    Returns:
        df (pd.DataFrame): returns a dataframe
            with ws_const.WINE_SCRAPER_OUTPUT_COLS
    """
    print("QUERYING page {}".format(page_num))
    query = HTML_FORMAT.format(page_num)
    response = requests.get(query)
    html_str = response.text
    xml_raw_product_data = html_str.split("product_id_")[1:]
    df = pd.DataFrame(xml_raw_product_data, columns=["RAW_DATA_STR"])
    if df.empty:
        print("NO DATA found, returning empty df.")
        return pd.DataFrame()

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
    df["RAW_DATA_STR"] = df["RAW_DATA_STR"].str.replace("\n", "")

    df["NAME"] = df["RAW_DATA_STR"].str.findall(
        r"(?<=js-elip-multi'>).*?(?=<)")
    # str.findall returns a list of one element, flatten this
    df["NAME"] = df["NAME"].apply(lambda x: x[0])

    # this should return a list of two prices [sale price, reg. price]
    regex = r"\$\d{1,3}(?:[,]\d{3})*(?:[.]\d{2})"
    #       |--|------|------------|-----------|
    #       |$ | 1-3  | 3 digits   | 2 digits  |
    #       |  |digits| repeated   |  (cents)  |
    #       |  |      |            |           |
    df["PRICES"] = df["RAW_DATA_STR"].str.findall(regex)
    df["PRICE"] = df["PRICES"].apply(lambda x: x[0][1:].replace(",", ""))
    df["BASE_PRICE"] = df["PRICES"].apply(lambda x: x[1][1:].replace(",", ""))

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
    now = pd.to_datetime("today").strftime("%Y%m%d_%H%M%S%f")
    out_file = "winelibrary_catalog_{}.csv".format(now)
    df.to_csv(os.path.join(settings.DATA_DIRECTORY, out_file), index=False)


def scrape():
    """Main scrape method.

    """
    df = query_all_pages()
    now = pd.to_datetime("today").strftime("%Y%m%d_%H%M%S%f")
    out_file = "winelibrary_catalog_{}.csv".format(now)
    df.to_csv(os.path.join(settings.DATA_DIRECTORY, out_file), index=False)


if __name__ == "__main__":
    scrape()
