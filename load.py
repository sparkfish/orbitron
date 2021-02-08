from os import getenv
from dotenv import load_dotenv
load_dotenv()
import sys
import io
import logging
log = logging.getLogger()

def setup_logger(log_level=logging.DEBUG):
    # setup logging to console output
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(handler)
    return logger

# todo: pull from URL rather than filesystem
#import requests

import numpy as np
import pandas as pd

from neighbor.storage import Storage

import json

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print("A filename must be provided")
        quit()

    log = setup_logger()

    storage = Storage()
    storage.connect()

    df = pd.read_csv(sys.argv[1], ',',keep_default_na=False, header=None)

    storage.execute_batch_neighborlocation_insert(df)

    storage.setup_neighbor_geometry()