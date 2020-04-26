"""All unit tests for scraper_io module.

"""

# STANDARD LIB
import os
import pandas as pd
import pytest

# PROJECT LIB
from scraper.settings import settings
from scraper.util import scraper_io


def test_to_sqlite_db_001():
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    scraper_io.to_sqlite_db(df, "TEST_TABLE",
                            os.path.join(settings.DB_DIRECTORY, "test_db.db"))


@pytest.mark.xfail(reason="No column C in existing table.")
def test_to_sqlite_db_002():
    df = pd.DataFrame({"C": [1, 2, 3], "B": [4, 5, 6]})
    scraper_io.to_sqlite_db(df, "TEST_TABLE",
                            os.path.join(settings.DB_DIRECTORY, "test_db.db"))


def test_to_sqlite_db_003():
    df = pd.DataFrame({"A": ["x", "y", "z"], "B": [4, 5, 6]})
    scraper_io.to_sqlite_db(df, "TEST_TABLE",
                            os.path.join(settings.DB_DIRECTORY, "test_db.db"))
