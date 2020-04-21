"""Scraper module for buyritewines.com.

"""

# STANDARD LIB
import os
import pandas as pd

# PROJECT LIB
from scraper.settings import settings

HTML = "https://www.buyritewines.com/wines/"
HTML_FORMAT = HTML + "?page={}&l={}"  # need a page number and result size


def query_one_page(page_num, results_per_page):
    print("QUERYING page {} with {} results per page".format(
        page_num, results_per_page))
    query = pd.read_html(HTML_FORMAT.format(page_num, results_per_page))
    df = pd.concat(query)
    if 4 not in df:
        print("NO DATA found, returning empty df.")
        return pd.DataFrame()

    df = df.loc[df[4].notnull(), [4]]  # data is in every few rows
    df.columns = ["RAW_DATA_STR"]
    df["PAGE_NUM"] = page_num

    df = get_metadata_from_query_result(df)
    df = df[df["NAME"].notnull()].reset_index(drop=True)

    df = df[["NAME", "PRICE", "BASE_PRICE", "IS_ON_SALE"]]
    return df


def query_all_pages(results_per_page, max_page_num=None):
    all_dfs = []
    if max_page_num is not None:
        for page_num in range(1, max_page_num + 1):
            df = query_one_page(page_num, results_per_page)
            all_dfs.append(df)

    else:
        page_num = 1
        while True:
            df = query_one_page(page_num, results_per_page)
            if not df.empty:
                all_dfs.append(df)
                page_num += 1
            else:
                break

    return pd.concat(all_dfs, ignore_index=True)


def get_metadata_from_query_result(df):
    df["NAME"] = df["RAW_DATA_STR"].str.findall("content_name.*?,").apply(
        lambda x: x[0].split(":")[1][:-1].strip() if x else None)

    df["PRICE"] = df["RAW_DATA_STR"].str.findall("item_price.*?\}").apply(
        lambda x: x[0].split(":")[1][:-2].replace(",", "") if x else None)
    df["PRICE"] = df["PRICE"].astype(float)

    df["BASE_PRICE"] = df["RAW_DATA_STR"].str.findall("\(Reg.*?\)").apply(
        lambda x: x[0].split("$")[1][:-1].replace(",", "") if x else None)
    df["BASE_PRICE"] = df["BASE_PRICE"].astype(float)

    df["BASE_PRICE"] = df["PRICE"].where(df["BASE_PRICE"].isnull(),
                                         df["BASE_PRICE"])

    df["IS_ON_SALE"] = df["BASE_PRICE"] != df["PRICE"]

    return df


if __name__ == "__main__":
    df = query_all_pages(100)
    now = pd.to_datetime("today").strftime("%Y%m%d_%H%M%S%f")
    out_file = "buyritewines_catalog_{}.csv".format(now)
    df.to_csv(os.path.join(settings.DATA_DIRECTORY, out_file))
