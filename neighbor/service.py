from os import getenv
from dotenv import load_dotenv
load_dotenv()
import json
import io
import logging
log = logging.getLogger()

from neighbor.storage import Storage


class NeighborService:

    def __init__(self):
        self.storage = Storage()


    def __enter__(self):
        self.storage.connect()

        return self


    def __exit__(self, exception, exception_value, tb):
        if tb:
            log.error(f"An error occurred: {exception}: {exception_value}")

        self.storage.disconnect()

    def getNearestNeighbor(self, count: int, sourceType: str, postalCode: str, miles: int):
        log.info(f"Getting {count} nearest {sourceType} to postal code {postalCode}")
        neighbors = self.storage.get_neighbors_by_zip(count, sourceType, postalCode, miles)
        for neighbor in neighbors:
            rowdata = json.loads(neighbor['rowdata'])

            ziplen = len(rowdata['zip'])

            # dirty hack to prepend lost leading zeroes
            if ziplen == 4 or ziplen == 8:
                rowdata['zip'] = "0" + rowdata['zip']

            neighbor.update(rowdata)
            neighbor.pop("rowdata")

        return neighbors
