"""Scraper module for garyswine.com.

"""

# STANDARD LIB
import os
import pandas as pd

# PROJECT LIB
from scraper.settings import settings

HTML = "https://www.garyswine.com/wines/"
HTML_FORMAT = HTML + "?page={}&l={}"  # need a page number and result size


def get_num_pages_and_results_per_page():
    # this returns a list of dfs
    first_query_results = pd.read_html(HTML)

    # determine number of pages to search through and maximum number
    # of results per page; this is all found in the second df
    df_page_info = first_query_results[1]
    print("PAGE_INFO: \n{}\n".format(df_page_info))

    max_results_per_page = int(df_page_info[1].to_string().split(" ")[-1])
    print("MAX_RESULTS_PER_PAGE: {}".format(max_results_per_page))

    first_col = df_page_info[0].to_string()
    num_items = int(first_col.split("|")[0].strip().split(" ")[-1])
    print("ALL ITEMS: {}".format(num_items))

    num_pages = num_items // max_results_per_page + 1
    print("DERIVED NUMBER OF PAGES: {}".format(num_pages))

    return num_pages, max_results_per_page


def query_one_page(page_num, results_per_page):
    print("QUERYING page {} with {} results per page".format(
        page_num, results_per_page))
    query = pd.read_html(HTML_FORMAT.format(page_num, results_per_page))
    df = pd.concat(query[2:-2])
    df.columns = ["METADATA", "JAVASCRIPT_DUMP"]
    df["PAGE_NUM"] = page_num

    df = get_name_and_price_from_query_result(df)
    df = df[df["NAME"].notnull()].reset_index(drop=True)

    df = df[["NAME", "PRICE"]]
    return df


def query_all_pages(max_page_num, results_per_page):
    all_dfs = []
    for page_num in range(1, max_page_num + 1):
        df = query_one_page(page_num, results_per_page)
        all_dfs.append(df)
    return pd.concat(all_dfs, ignore_index=True)


def get_name_and_price_from_query_result(df):
    def get_name(x):
        try:
            name = [a.strip() for a in x.split(",") if "content_name" in a][0]
            name = name.split(":")[1].strip()
            return name
        except:
            return None

    df["NAME"] = df["JAVASCRIPT_DUMP"].apply(get_name)

    def get_price(x):
        try:
            price = [a.strip() for a in x.split(",") if "item_price" in a][0]
            price = price.split(":")[1].split(" ")[0].strip()
            price = float(price)
            return price
        except:
            return None

    df["PRICE"] = df["JAVASCRIPT_DUMP"].apply(get_price)

    return df


if __name__ == "__main__":
    num_pages, max_results_per_page = get_num_pages_and_results_per_page()
    df = query_all_pages(num_pages, max_results_per_page)
    # df = query_one_page(9, 100)

    now = pd.to_datetime("today").strftime("%Y%m%d_%H%M%S%f")
    out_file = "garyswine_catalog_{}.csv".format(now)
    df.to_csv(os.path.join(settings.DATA_DIRECTORY, out_file))
