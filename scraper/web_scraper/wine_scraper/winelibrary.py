"""Scraper module for winelibrary.com.

"""

# STANDARD LIB
import bs4
import os
import pandas as pd
import requests

# PROJECT LIB
from scraper.settings import settings

HTML = "https://winelibrary.com/search"
HTML_FORMAT = HTML + "?page={}"  # need a page number


def query_one_page(page_num):
    print("QUERYING page {}".format(page_num))
    response = requests.get(HTML_FORMAT.format(page_num))
    html_str = response.text
    xml_raw_product_data = html_str.split("product_id_")[1:]
    df = pd.DataFrame(xml_raw_product_data, columns=["RAW_DATA_STR"])

    df = get_metadata_from_query_result(df)
    df = df[df["NAME"].notnull()].reset_index(drop=True)

    df = df[["NAME", "PRICE", "BASE_PRICE", "IS_ON_SALE"]]
    return df


def query_all_pages(max_page_num=None):
    all_dfs = []
    if max_page_num is not None:
        for page_num in range(1, max_page_num + 1):
            df = query_one_page(page_num, )
            all_dfs.append(df)

    else:
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
    df["NAME"] = df["RAW_DATA_STR"].str.findall("(?<=js-elip-multi'>).*?(?=<)")
    # str.findall returns a list of one element, flatten this
    df["NAME"] = df["NAME"].apply(lambda x: x[0])

    df["RAW_DATA_STR"] = df["RAW_DATA_STR"].str.replace("\n", "")
    df["PRICES"] = df["RAW_DATA_STR"].str.findall(
        "\$\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})")

    to_float = lambda x: float(x[0][1:].replace(",", ""))
    df["PRICE"] = df["PRICES"].apply(to_float)
    df["BASE_PRICE"] = df["PRICES"].apply(to_float)

    df["IS_ON_SALE"] = df["BASE_PRICE"] != df["PRICE"]
    return df


if __name__ == "__main__":
    df = query_all_pages()
    now = pd.to_datetime("today").strftime("%Y%m%d_%H%M%S%f")
    out_file = "winelibrary_catalog_{}.csv".format(now)
    df.to_csv(os.path.join(settings.DATA_DIRECTORY, out_file))