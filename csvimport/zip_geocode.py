from os import getenv
from dotenv import load_dotenv
load_dotenv()

import io
import logging
log = logging.getLogger()

# todo: pull from URL rather than filesystem
#import requests

import numpy as np
import pandas as pd

from neighbor.storage import Storage


class ZipGeocodeImporter:

    def __init__(self):
        self.storage = Storage()
        self.storage.connect()
		
    def __exit__(self, exception, exception_value, tb):
        if tb:
            log.error(f"An error occurred: {exception}: {exception_value}")

    def importCsv(self):
        df = pd.read_csv('./US.txt', '\t', header=None, keep_default_na=False,
        names=["CountryCode","PostalCode","PlaceName","AdminName1","AdminCode1","AdminName2","AdminCode2","AdminName3","AdminCode3","Latitude","Longitude","Accuracy"],
        dtype={"CountryCode":np.str,"PostalCode":np.str,"PlaceName":np.str,"AdminName1":np.str,"AdminCode1":np.str,"AdminName2":np.str,
        "AdminCode2":np.str,"AdminName3":np.str,"AdminCode3":np.str,"Latitude":np.str,"Longitude":np.str,"Accuracy":np.str})

        df['Accuracy'] = df['Accuracy'].replace('', '-1') 

        self.storage.execute_batch_zipgeodata_insert(df)
