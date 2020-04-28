"""Module of input / output tools.

"""

# STANDARD LIB
import os
import sqlite3
import pandas as pd

# PROJECT LIB
from scraper.settings import settings


def to_sqlite_db(df, table_name, db_path):
    """Writes a dafa frame to the given table and sqlite db.

    Args:
        df (pd.DataFrame): data frame in the correct table structure.
        table_name (str): name of the table to write data to.
        db_path (str): path of the sqlite database.

    Returns:
        void
    """
    try:
        cnx = sqlite3.connect(db_path)
    except ConnectionError as e:
        print("Failed to connect to sqlite db: {}".format(e))
        raise

    df.to_sql(name=table_name, con=cnx, if_exists="append", index=False)


def to_csv(df, basename):
    """Writes a dafa frame to a csv file.

    Args:
        df (pd.DataFrame): data frame in the correct table structure.
        basename (str): name of the file (no extension) to write data to.

    Returns:
        void
    """
    now = pd.to_datetime("today").strftime("%Y%m%d_%H%M%S%f")
    out_file = "{}_{}.csv".format(basename, now)
    df.to_csv(os.path.join(settings.DATA_DIRECTORY, out_file), index=False)
