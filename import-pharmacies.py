from os import getenv
from dotenv import load_dotenv
load_dotenv()

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
    log = setup_logger()

    storage = Storage()
    storage.connect()
	
    sourceId = storage.insert_source("pharmacies")

    csvDf = pd.read_csv('./facility.csv', ',',keep_default_na=False, dtype={"CalcLocation":str,"Name":str,"Address":str,"City":str,"State":str,"Zip":str,"formated_phone":str,"Status":str,"Icon":str,"Type":str})
        
    df = pd.DataFrame()
    df["SourceId"] = sourceId
    df["Name"] = csvDf["Name"]
    coords = csvDf["CalcLocation"].str.split(",", n=1, expand=True)
    df["Latitude"] = coords[0]
    df["Longitude"] = coords[1]
    df["RowData"] = '{}'
    for i, row in df.iterrows():
        df.at[i, "SourceId"] = sourceId
        df.at[i, "RowData"] = json.dumps( {
        ('phone'): csvDf.at[i, "formated_phone"],
        ('address'): csvDf.at[i, "Address"],
        ('city'): csvDf.at[i, "City"],
        ('state'): csvDf.at[i, "State"],
        ('zip'): csvDf.at[i, "Zip"]
        } )

    storage.execute_batch_neighborlocation_insert(df)

    storage.setup_neighbor_geometry()