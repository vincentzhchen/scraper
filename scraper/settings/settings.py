# STANDARD LIB
import importlib.util
import os
import sys

homedir = os.path.expanduser("~")
homedir = os.path.realpath(homedir)
scraper_config_dir = os.path.join(homedir, ".scraper")
scraper_config_path = os.path.join(scraper_config_dir, "scraper_config.py")

config_path = scraper_config_path
if os.path.exists(scraper_config_path):
    spec = importlib.util.spec_from_file_location("scraper", config_path)
    c = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(c)

    # Setup constants.
    DATA_DIRECTORY = c.DATA_DIRECTORY
    DB_DIRECTORY = c.DB_DIRECTORY
else:
    print("No configuration file found... exiting process...")
    sys.exit(1)
