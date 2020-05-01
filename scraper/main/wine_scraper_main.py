"""Driver file for all the wine_scraper modules.

"""

# STANDARD LIB
import argparse
import os
import pandas as pd

# PROJECT LIB
from scraper.settings import settings
from scraper.web_scraper.wine_scraper import (allendalewine, buyritewines,
                                              garyswine, winelibrary)
from scraper.util import scraper_io


def scrape(run_id, module):
    """Scrape to db.

    Include database audit columns and run ID here.

    Args:
        run_id (int): ID of this run.
        module (module): a wine_scraper module.

    """
    try:
        name = module.__name__.split(".")[-1]
        print("Scraping {}...".format(name))
        df = module.scrape()
        cols = df.columns.tolist()
        df["RUN_ID"] = run_id
        df = df[["RUN_ID"] + cols]
        scraper_io.to_sqlite_db(df,
                                table_name="wine",
                                db_path=os.path.join(settings.DB_DIRECTORY,
                                                     "wine_db.db"))
    except Exception as e:
        print("Failed to scrape {} into db, exception {}".format(name, e))


def main():
    """Scrape everything.

    """
    run_id = int(pd.to_datetime("today").strftime("%Y%m%d%H%M%S"))

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--scraper_to_run")
    args = parser.parse_args()

    if args.scraper_to_run is None or args.scraper_to_run == "allendalewine":
        scrape(run_id, allendalewine)
    if args.scraper_to_run is None or args.scraper_to_run == "buyritewines":
        scrape(run_id, buyritewines)
    if args.scraper_to_run is None or args.scraper_to_run == "garyswine":
        scrape(run_id, garyswine)
    if args.scraper_to_run is None or args.scraper_to_run == "winelibrary":
        scrape(run_id, winelibrary)


if __name__ == "__main__":
    main()
