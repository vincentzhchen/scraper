"""Module of input / output tools.

"""

# STANDARD LIB
import sqlite3


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
