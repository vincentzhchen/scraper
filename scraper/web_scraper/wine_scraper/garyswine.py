"""Scraper module for garyswine.com.

"""

# STANDARD LIB
import os
import pandas as pd

# PROJECT LIB
from scraper.settings import settings

HTML = "https://www.garyswine.com/"
HTML_FORMAT = HTML + "wines/?page={}&l={}"  # need a page number and result size

RESULTS_PER_PAGE = 100  # easier if constant


def query_one_page(page_num):
    print("QUERYING page {}".format(page_num))
    query = HTML_FORMAT.format(page_num, RESULTS_PER_PAGE)
    result = pd.read_html(query)
    df = pd.concat(result[2:-2])
    df.columns = ["METADATA", "RAW_DATA_STR"]
    df = df[["RAW_DATA_STR"]].dropna()

    df["SRC"] = HTML
    df["QUERY"] = query
    df["AS_OF_DATE"] = pd.to_datetime("today")

    df = get_metadata_from_query_result(df)

    df = df[["NAME", "PRICE", "BASE_PRICE", "IS_ON_SALE", "SRC", "QUERY",
             "AS_OF_DATE"]]
    return df


def query_all_pages():
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
    df["NAME"] = df["RAW_DATA_STR"].str.findall("content_name.*?,").apply(
        lambda x: x[0].split(":")[1][:-1].strip() if x else None)

    df = df[df["NAME"].notnull()].copy()

    # this should return a list of one price [reg. price] if no sale and
    # two prices [sale price, reg. price] if sale
    regex = "\$\d{1,3}(?:[,]\d{3})*(?:[.]\d{2})"
    """
            |--|------|------------|-----------|
            |$ | 1-3  | 3 digits   | 2 digits  |
            |  |digits| repeated   |  (cents)  |
            |  |      |            |           |
    """
    df["PRICES"] = df["RAW_DATA_STR"].str.findall(regex)
    df["PRICE"] = df["PRICES"].apply(lambda x: x[0][1:].replace(",", ""))
    df["BASE_PRICE"] = df["PRICES"].apply(
        # if one price, then take the single listed price
        lambda x: x[1][1:].replace(",", "") if (
            x[1:2]) else x[0][1:].replace(",", ""))

    df["IS_ON_SALE"] = df["BASE_PRICE"] > df["PRICE"]

    return df


if __name__ == "__main__":
    #df = query_all_pages()
    df = query_one_page(9)

    now = pd.to_datetime("today").strftime("%Y%m%d_%H%M%S%f")
    out_file = "garyswine_catalog_{}.csv".format(now)
    df.to_csv(os.path.join(settings.DATA_DIRECTORY, out_file), index=False)
